from flask import flash, redirect, render_template, url_for, request, session
from flask_login import current_user, login_required
from sqlalchemy.exc import IntegrityError

from .. import shop

from ... import db
from ...models import Cart, Product
from ...view_models import CartItem

from decimal import Decimal

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
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(user_id=current_user.id)
        quantities = {x.product_id: x.quantity for x in cart_items.all()}
    else:
        quantities = guest_cart()
    products = Product.query.filter(Product.id.in_(list(quantities.keys()))).all()
    cart_item_vms = []
    for x in products:
        if current_user.is_authenticated:
            q = quantities[x.id]
        else:
            q = quantities[str(x.id)]['quantity']
        cart_item_vm = CartItem(x.name, x.price, x.quantity, q*x.price, x.id, x.main_image)

        # check if price has changed
        if current_user.is_authenticated:
            cart_item = cart_items.filter_by(product_id=x.id).first()
            if cart_item.price != x.price:
                flash('The price for {} has changed from {} to {}!'.format(x.name,
                                                                        cart_item.price,
                                                                        x.price),
                                                                        'warning')
                # XXX: Should you update the price and ignore warning, after 1 request?
                #cart_item.price = x.price
                #try:
                #    db.session.merge(cart_item)
                #    db.session.commit()
                #except:
                #    pass #do it next time
        else:
            old_price = Decimal(quantities[str(x.id)]['price'])
            new_price = x.price
            if new_price != old_price:
                flash('The price for {} has changed from {} to {}!'.format(x.name,
                                                                        old_price,
                                                                        new_price),
                                                                        'warning')
                #quantities[str(x.id)]['price'] = str(new_price)

        # check if quantity has changed
        if x.quantity == 0:
            flash('{} has become unavailable so it won\'t be part of your order'.format(x.name), 'warning')
            if current_user.is_authenticated:
                cart_item = cart_items.filter_by(product_id=x.id).first()
                if not cart_item:
                    print('Item has become unavailable??????') # TODO: WHAT?
                if cart_item.quantity > 0:
                    cart_item.quantity = x.quantity
                    try:
                        db.session.merge(cart_item)
                        db.session.commit()
                    except:
                        raise
                        # TODO:
            else:
                if q > 0:
                    quantities[str(x.id)] = x.quantity
                    #session['cart'] = quantities

                

            cart_item_vm.quantity = 0
            cart_item_vm.total = Decimal(0.)
            cart_item_vm.price = Decimal(0.)
        elif x.quantity - q < 0:
            # XXX: BUG
            flash('You order quantity for item {} has been reduced due to decreased availability'.format(x.name), 'warning')
            if current_user.is_authenticated:
                cart_item = cart_items.filter_by(product_id=x.id).first()
                cart_item.quantity = x.quantity
                try:
                    db.session.merge(cart_item)
                    db.session.commit()
                except:
                    raise
                    # TODO:
            else:
                quantities[str(x.id)] = x.quantity

            cart_item_vm.total = x.quantity*x.price
        else:
            if q == 0:
                flash('Item {} has become available. You can now restore your order'.format(x.name), 'info')
            cart_item_vm.quantity = q
            cart_item_vm.total = q*x.price
        cart_item_vms.append(cart_item_vm)
    
    total = sum([x.total for x in cart_item_vms])
    return render_template('shop/cart.html', products=cart_item_vms, total=total, title="Cart")

@shop.route('/cart/add/<int:id>', methods=['GET','POST'])
def add_to_cart(id):
    """
    Add a product to cart
    """
    def do_work(item):
        product = Product.query.filter_by(id=item.product_id).first()
        if product.quantity <= 0:
            flash('This item is currently unavailable.', 'warning')
        if item.quantity + 1 > product.quantity:
            flash('You can not add more from this product.', 'warning')
        else:
            item.quantity += 1
            if current_user.is_authenticated:
                db.session.merge(item)
                db.session.commit()
            else:
                session['cart'][str(product.id)]['quantity'] += 1
            flash('Cart item updated.', 'info')
    
    def not_found():
        product = Product.query.filter_by(id=id).first()
        if current_user.is_authenticated:
            item = Cart(user_id=current_user.id, product_id=id, price=product.price)
            try:
                db.session.add(item)
                db.session.commit()
                flash('Item added to cart.', 'info')
            except IntegrityError:
                flash('Invalid item.', 'warning')
            except:
                raise
                flash('Sorry, you can\'t do that right now.', 'warning')
        else:
            try:
                cart = session['cart']
            except KeyError:
                cart = {}
            cart[str(id)] = {}
            cart[str(id)]['price'] = str(product.price)
            cart[str(id)]['quantity'] = 1
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

            flash('Item removed from cart.', 'info')
        except:
            flash('Sorry, you can\'t do that at the moment.', 'warning')
    
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
                session['cart'][str(id)]['quantity'] -= 1
            flash('Cart item updated.', 'info')
        elif item.quantity == 1:
            if current_user.is_authenticated:
                db.session.delete(item)
                db.session.commit()
            else:
                del session['cart'][str(id)]
    
    handle_item(id, do_work)

    return redirect(url_for('shop.cart'))

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
        flash('You have emptied your cart.', 'info')
    except:
        raise
        flash('Sorry, you can\'t do that at the moment.', 'warning')
    
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
        try:
            if str(id) in session['cart']:
                item = Cart(user_id=None, product_id=id, quantity=session['cart'][str(id)]['quantity'])
        except KeyError:
            pass

    if item:
        # do the work
        do_work(item)
    else:
        if not not_found:
            flash('Item not found in your cart.', 'warning')
        else:
            not_found() 


