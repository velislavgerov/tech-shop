from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from . import cart

from .. import db
from ..models import Cart, Product

@cart.route('/cart', methods=['GET','POST'])
@login_required
def list_items():
    """
    List all items in cart
    """
    product_ids = Cart.query.filter_by(user_id = current_user.id).all()
    product_ids = [x.product_id for x in product_ids]
    print(product_ids)
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    
    return render_template('cart/cart.html', products=products, title="Cart")

@cart.route('/cart/add/<int:id>', methods=['GET','POST'])
@login_required
def add_to_cart(id):
    """
    Add a product to cart
    """
    # XXX:check_admin - should they have a cart?
    # XXX: product_id should be checked
    cart = Cart(user_id=current_user.id,
                product_id=id)
    try:
        db.session.merge(cart)
        db.session.commit()
        flash('Item added.')
    except:
        flash('Item already in your shopping cart.')

    return redirect(url_for('home.homepage'))

@cart.route('/cart/remove/<int:id>', methods=['GET','POST'])
@login_required
def remove_item(id):
    """
    Removes an item from the cart
    """
    # XXX: Pottential point of failure if two or more items were to be found
    item = Cart.query.filter(Cart.user_id == current_user.id).filter(Cart.product_id == id).one()
    print(item)
    db.session.delete(item)
    db.session.commit()
    
    return redirect(url_for('cart.list_items'))
