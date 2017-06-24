from flask import flash, redirect, render_template, url_for, request
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

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
    def do_work(item):
        product = Product.query.filter_by(id=item.product_id).first()
        if item.quantity + 1 > product.quantity:
            flash('You can not add more from this product.')
        else:
            item.quantity += 1
            db.session.merge(item)
            db.session.commit()
            flash('Item updated.')
    
    def not_found():
        item = Cart(user_id=current_user.id, product_id=id)
        try:
            db.session.add(item)
            db.session.commit()
            flash('Item added.')
        except IntegrityError:
            flash('Invalid item.')
        except:
            flash('Sorry, you can\'t do that right now.')

    handle_item(id, do_work, not_found) 
 
    return redirect(url_for('cart.list_items'))

@cart.route('/cart/remove/<int:id>', methods=['GET','POST'])
@login_required
def remove_item(id):
    """
    Removes an item from the cart
    """
    def do_work(item):
        try:
            db.session.delete(item)
            db.session.commit()
        except:
            flash('Sorry, you can\'t do that at the moment.')
    
    handle_item(id, do_work)
    
    return redirect(url_for('cart.list_items'))

@cart.route('/cart/remove/one/<int:id>', methods=['GET','POST'])
@login_required
def remove_one_item(id):
    """
    Decrements item count from the cart
    """
    def do_work(item):
        if item.quantity > 1:
            item.quantity -= 1
            db.session.merge(item)
            db.session.commit()
            flash('Item updated.')
        elif item.quantity == 1:
            db.session.delete(item)
            db.session.commit()
    
    handle_item(id, do_work)

    return redirect(url_for('cart.list_items'))

@cart.route('/cart/empty', methods=['GET','POST'])
@login_required
def empty_cart():
    """
    Removes all items from user's cart
    """
    try:
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        flash('You have emptied your cart.')
    except:
        raise
        flash('Sorry, you can\'t do that at the moment.')
    
    return redirect(url_for('cart.list_items'))

def handle_item(id, do_work, not_found=None):
    """
    Helper function to handle our work with the cart items.
    """
    # XXX: There is just one intended way for this to work, but should I handle
    # errors?  
    item = Cart.query.filter(Cart.user_id == current_user.id).filter(Cart.product_id == id).first()
    if item:
        # do the work
        do_work(item)
    else:
        if not not_found:
            flash('Item not found in your cart.')
        else:
            not_found()
        


