from flask import flash, redirect, render_template, url_for, request, session
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from .. import shop

from ... import db
from ...models import Cart, Product

def guest_cart():
    try:
        return session['cart']
    except KeyError:
        session['cart'] = {}
        return session['cart']

@shop.route('/cart', methods=['GET','POST'])
def cart():
    """
    List all items in cart
    """
    # TODO: SHOULD CHECK PRODUCT AVAILABILITY AND FILTER UNAVAILABLE
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(customer_id=current_user.id).all()
        quantities = {x.product_id: x.quantity for x in cart_items}
    else:
        quantities = guest_cart()
    products = Product.query.filter(Product.id.in_(list(quantities.keys()))).all()
    for x in products:
        if current_user.is_authenticated:
            q = quantities[x.id]
        else:
            q = quantities[str(x.id)]
        x.quantity = q
        x.price = q*x.price
    total = None
    if products:
        total = sum([x.price for x in products])
    return render_template('shop/cart.html', products=products, total=total, title="Cart")

@shop.route('/cart/add/<int:id>', methods=['GET','POST'])
def add_to_cart(id):
    """
    Add a product to cart
    """
    def do_work(item):
        product = Product.query.filter_by(id=item.product_id).first()
        if product.quantity <= 0:
            flash('This item is currently unavailable.')
        if item.quantity + 1 > product.quantity:
            flash('You can not add more from this product.')
        else:
            item.quantity += 1
            if current_user.is_authenticated:
                db.session.merge(item)
                db.session.commit()
            else:
                session['cart'][str(product.id)] += 1
            flash('Item updated.')
    
    def not_found():
        if current_user.is_authenticated:
            item = Cart(user_id=current_user.id, product_id=id)
            try:
                db.session.add(item)
                db.session.commit()
                flash('Item added.')
            except IntegrityError:
                flash('Invalid item.')
            except:
                raise
                flash('Sorry, you can\'t do that right now.')
        else:
            cart = session['cart']
            cart[str(id)] = 1
            session['cart'] = cart

    handle_item(id, do_work, not_found) 
 
    return redirect(url_for('shop.cart'))

@shop.route('/cart/remove/<int:id>', methods=['GET','POST'])
def remove_cart_item(id):
    """
    Removes an item from the cart
    """
    def do_work(item):
        try:
            if current_user.is_authenticated:
                db.session.delete(item)
                db.session.commit()
            else:
                del session['cart'][str(id)]

            flash('Item removed.')
        except:
            flash('Sorry, you can\'t do that at the moment.')
    
    handle_item(id, do_work)
    
    return redirect(url_for('shop.cart'))

@shop.route('/cart/remove/one/<int:id>', methods=['GET','POST'])
def remove_one_cart_item(id):
    """
    Decrements item count from the cart
    """
    def do_work(item):
        if item.quantity > 1:
            item.quantity -= 1
            if current_user.is_authenticated:
                db.session.merge(item)
                db.session.commit()
            else:
                session['cart'][str(id)] -= 1
            flash('Item updated.')
        elif item.quantity == 1:
            if current_user.is_authenticated:
                db.session.delete(item)
                db.session.commit()
            else:
                del session['cart'][str(id)]
    
    handle_item(id, do_work)

    return redirect(url_for('cart.list_items'))

@shop.route('/cart/empty', methods=['GET','POST'])
def empty_cart():
    """
    Removes all items from user's cart
    """
    try:
        if current_user.is_authenticated:
            Cart.query.filter_by(user_id=current_user.id).delete()
        else:
            session['cart'] = {}
        db.session.commit()
        flash('You have emptied your cart.')
    except:
        raise
        flash('Sorry, you can\'t do that at the moment.')
    
    return redirect(url_for('shop.cart'))

def handle_item(id, do_work, not_found=None):
    """
    Helper function to handle our work with the cart items.
    """
    # XXX: There is just one intended way for this to work, but should I handle
    # errors?
    item = None
    if current_user.is_authenticated:
        item = Cart.query.filter(Cart.user_id == current_user.id).filter(Cart.product_id == id).first()
    else:
        if session['cart']:
            if str(id) in session['cart']:
                item = Cart(user_id=None, product_id=id, quantity=session['cart'][str(id)])

    if item:
        # do the work
        do_work(item)
    else:
        if not not_found:
            flash('Item not found in your cart.')
        else:
            not_found() 


