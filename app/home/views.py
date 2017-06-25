from flask import abort, flash, render_template, request, url_for, redirect
from flask_login import current_user, login_required

from ..models import Product, Category, Cart, Address, OrderDetail
from .. import db

from ..auth.forms import AccountForm

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

@home.route('/order/confirm', methods=['GET', 'POST'])
@login_required
def confirm_order():
    """
    Render the order page
    """

    form = AccountForm()
    address = Address.query.filter_by(user_id=current_user.id).first()
    if form.validate_on_submit():
        if not address:
            address = Address(user_id=current_user.id)
        address.tel_number = form.tel_number.data
        address.address_line_1 = form.address_line_1.data
        address.address_line_2 = form.address_line_2.data
        address.city = form.city.data
        address.county = form.county.data
        address.postcode = form.postcode.data
        address.country = form.country.data
        try:
            db.session.merge(address)
            db.session.commit()
            flash('You have succesfully confirmed your details.')
            return redirect(url_for('home.finalize_order'))
        except:
            flash('Sorry, you can\'t do this right now.')
    
    form.email.data = current_user.email
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    if address:
        form.tel_number.data = address.tel_number
        form.address_line_1.data = address.address_line_1
        form.address_line_2.data = address.address_line_2
        form.city.data = address.city
        form.county.data = address.county
        form.postcode.data = address.postcode
        form.country.data = address.country
    form.submit.label.text = "Confirm"

    return render_template('home/confirm_order.html', form=form, title="Confirm Details")

@home.route('/order/finalize', methods=['GET', 'POST'])
@login_required
def finalize_order():
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

    return render_template('home/pay_order.html', products=products, total=total, title="Finalize Order")
