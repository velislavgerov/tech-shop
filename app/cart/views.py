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
    product_ids = {x.product_id: x.quantity for x in product_ids}
    products = Product.query.filter(Product.id.in_(list(product_ids.keys()))).all()
    for x in products:
        x.quantity = product_ids[x.id]
    total = None
    if products:
        total = sum([x.price*x.quantity for x in products])
    return render_template('cart/cart.html', products=products, total=total, title="Cart")

@cart.route('/cart/add/<int:id>', methods=['GET','POST'])
@login_required
def add_to_cart(id):
    """
    Add a product to cart
    """
    # get item, reurns None if item does not exist already
    item = Cart.query.filter_by(user_id=current_user.id).filter_by(product_id=id).first()
    if item: # was found
        product = Product.query.filter_by(id=item.product_id).first()
        if item.quantity + 1 > product.quantity:
            flash('You can not add more from this product.')
        else:
            item.quantity += 1
            db.session.merge(item)
            db.session.commit()
            flash('Item updated.')
    else:
        item = Cart(user_id=current_user.id,
                product_id=id)
        db.session.add(item)
        db.session.commit()
        flash('Item added.')

    return redirect(url_for('home.homepage'))

@cart.route('/cart/remove/<int:id>', methods=['GET','POST'])
@login_required
def remove_item(id):
    """
    Removes an item from the cart
    """
    item = Cart.query.filter(Cart.user_id == current_user.id).filter(Cart.product_id == id).first()
    if item:
        try:
            db.session.delete(item)
            db.session.commit()
        except:
            flash('Sorry, you can\'t do that at the moment.')
    else:
        flash('Item not found in your cart.')
    
    return redirect(url_for('cart.list_items'))

@cart.route('/cart/decrement/<int:id>', methods=['GET','POST'])
@login_required
def decrement_item(id):
    """
    Decrements item count from the cart
    """
    item = Cart.query.filter(Cart.user_id == current_user.id).filter(Cart.product_id == id).first()
    if item.quantity > 1:
        item.quantity -= 1
        db.session.merge(item)
        db.session.commit()
        flash('Decreased item count.')
    elif item.quantity == 1:
        db.session.delete(item)
        db.session.commit()
    
    return redirect(url_for('cart.list_items'))

@cart.route('/cart/increment/<int:id>', methods=['GET','POST'])
@login_required
def increment_item(id):
    """
    Removes an item from the cart
    """
    item = Cart.query.filter(Cart.user_id == current_user.id).filter(Cart.product_id == id).first()
    if item.quantity > 1:
        item.quantity -= 1
        db.session.merge(item)
        db.session.commit()
        flash('Decreased item count.')
    elif item.quantity == 1:
        db.session.delete(item)
        db.session.commit()
    
    return redirect(url_for('cart.list_items'))

