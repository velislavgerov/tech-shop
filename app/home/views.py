from flask import abort, flash, render_template, request, url_for, redirect
from flask_login import current_user, login_required

from ..models import Product, Category, Cart, Address, OrderDetail
from .. import db

from .forms import OrderDetailForm

from . import home

from datetime import datetime

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    search = request.args.get('search')
    category = request.args.get('category')
    categories = Category.query.all()
    if search:
        products = Product.query.filter(Product.name.like('%{}%'.format(search))).all()
    else:
        products = Product.query.all()
    if category:
        try:
            c_id = Category.query.filter_by(name = category).one()
            products = Product.query.filter_by(category_id = c_id.id).all()
        except:
            raise
    return render_template('home/index.html', categories=categories, products=products, title="Welcome")

@home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """
    Render the admin dashboard template on the /admin/dashboard route
    """
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)

    return render_template('home/admin_dashboard.html', title="Dashboard")

@home.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    """
    Render the order page
    """
    cart_items = Cart.query.filter_by(user_id=current_user.id).all()
    quantities = {x.product_id: x.quantity for x in cart_items}
    products = Product.query.filter(Product.id.in_(list(quantities.keys()))).all()
    for x in products:
        q = quantities[x.id]
        x.quantity = q
        x.price = q*x.price
    total = None
    if products:
        total = sum([x.price for x in products])

    form = OrderDetailForm()
    print(form.errors)
    if form.validate_on_submit():
        order_detail = OrderDetail(
                user_id=current_user.id,
                email=current_user.email,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                tel_number = form.tel_number.data,
                address_line_1 = form.address_line_1.data,
                address_line_2 = form.address_line_2.data,
                city = form.city.data,
                county = form.county.data,
                postcode = form.postcode.data,
                country = form.country.data,
                message = form.message.data,
                created_at = datetime.utcnow()
                )
        print(order_detail.id)
        try:
            db.session.add(order_detail)
            db.session.commit()
            flash('You have confirmed your order.')
            return redirect(url_for('home.homepage'))
        except:
            raise
            flash('Sorry, you can\'t do this right now.')
 
    form.email.data = current_user.email
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
 
    address = Address.query.filter_by(user_id=current_user.id).first()    
    if address:
        form.tel_number.data = address.tel_number
        form.address_line_1.data = address.address_line_1
        form.address_line_2.data = address.address_line_2
        form.city.data = address.city
        form.county.data = address.county
        form.postcode.data = address.postcode
        form.country.data = address.country

    return render_template('home/order.html', products=products, form=form, total=total, title="Order")
