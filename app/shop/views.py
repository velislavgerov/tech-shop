from flask import abort, flash, render_template, request, url_for, redirect
from flask_login import current_user, login_required

from ..models import Product, Category, Cart, Order
from .. import db

from ..customer.forms import AccountForm

from . import shop

from datetime import datetime

@shop.route('/')
def index():
    """
    Render the homepage template on the / route
    """
    search = request.args.get('search')
    category = request.args.get('category')
    sort = request.args.get('sort')
    categories = Category.query.all()
    if search:
        products_query = Product.query.filter(Product.name.ilike('%{}%'.format(search)))
    else:
        products_query = Product.query
    if category:
        try:
            c_id = Category.query.filter_by(name = category).first()
            if c_id:
                products_query = products_query.filter_by(category_id = c_id.id)
            flash('Non-existent category. Displaying results from all categories', 'info')
        except:
            raise

    if sort:
        if sort == 'price_desc':
            products = products_query.order_by(Product.price.desc()).all()
        elif sort == 'price_asc':
            products = products_query.order_by(Product.price.asc()).all()
        elif sort == 'name_desc':
            products = products_query.order_by(Product.name.desc()).all()
        else: #name_asc if name_asc or else
            products = products_query.order_by(Product.name.asc()).all()
    else:
        products = products_query.all()

    return render_template('shop/index.html', 
                            category=category,
                            search=search,
                            sort=sort,
                            categories=categories,
                            products=products,
                            title="Welcome")

@shop.route('/order/confirm', methods=['GET', 'POST'])
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
            return redirect(url_for('shop.finalize_order'))
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

    return render_template('shop/confirm_order.html', form=form, title="Confirm Details")

@shop.route('/order/finalize', methods=['GET', 'POST'])
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

    return render_template('shop/pay_order.html', products=products, total=total, title="Finalize Order")
