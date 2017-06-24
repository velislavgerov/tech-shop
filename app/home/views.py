from flask import abort, render_template, request
from flask_login import current_user, login_required

from ..models import Product, Category, Cart, Address
from ..auth.forms import AccountForm

from . import home

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

@home.route('/order')
@login_required
def order():
    """
    Render the order page
    """
    items = Cart.query.filter_by(user_id=current_user.id).all()
    product_ids = {x.product_id: x.quantity for x in items}
    products = Product.query.filter(Product.id.in_(list(product_ids.keys()))).all()
    for x in products:
        x.quantity = product_ids[x.id]
    total = None
    if products:
        total = sum([x.price*x.quantity for x in products])

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
            flash('You have succesfully updated your details.')
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

    return render_template('home/order.html', products=products, form=form, total=total, title="Order")
