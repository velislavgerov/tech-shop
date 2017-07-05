from flask import request, jsonify, abort, flash, render_template, request, url_for, redirect, session
from flask_login import current_user, login_required
from paypalrestsdk import Payment, WebProfile, Sale, ResourceNotFound

from . import payment

from ..models import Product, Category, Cart, Order, OrderItem, OrderStatus, User
from .. import db

from datetime import datetime
import random, string
from decimal import Decimal

def web_profile_id():
    # TODO: Use a single webprofile
    # Name needs to be unique so just generating a random one
    wpn = ''.join(random.choice(string.ascii_uppercase) for i in range(12))

    web_profile = WebProfile({
        "name": wpn,
        "presentation": {
            "brand_name": "Tech Shop",
            "locale_code": "US"
        },
        "input_fields": {
            "allow_note": True,
            "no_shipping": 0,
            "address_override": 1
        },
        "flow_config": {
            "landing_page_type": "billing"
        }
    })

    if web_profile.create():
        print(web_profile)
        print("Web Profile[%s] created successfully" % (web_profile.id))
        return web_profile.id
    else:
        print(web_profile.error)

@payment.route('/payment/create', methods=['POST'])
def create():
    """
    Create paypal payment
    """
    total = 0
    products = None
    items = []
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all() # POF
        quantities = {x.product_id: x.quantity for x in cart_items}
        products = Product.query.filter(Product.id.in_(list(quantities.keys()))).all() #POF
        if products:
            for x in products:
                wanted_quantity = quantities[x.id]
                if wanted_quantity == 0:
                    products.remove(x)
                    break
                if x.quantity - wanted_quantity < 0:
                    flash("One of the products in your order has become unavailable!", "danger")
                    response = jsonify(redirect_url=url_for('shop.cart'))
                    response.status_code = 302
                    return response
                total += x.price*wanted_quantity

            total = sum([x.price*quantities[x.id] for x in products])
        #ELSE?
    else:
        # Generate PayPal transactions data from the guest cart
        # Specifically, we currently use items and ammount
        cart_items = session['cart'] # POF
        products = Product.query.filter(Product.id.in_(list(cart_items.keys()))).all() #POF
        if products:
            for x in products:
                wanted_quantity = cart_items[str(x.id)]
                if wanted_quantity == 0:
                    products.remove(x)
                    break
                if x.quantity - wanted_quantity < 0:
                    flash("One of the products in your order has become unavailable!", "danger")
                    response = jsonify(redirect_url=url_for('shop.cart'))
                    response.status_code = 302
                    return response
                total += x.price*wanted_quantity
            # total = sum([x.price*cart_items[str(x.id)] for x in products])
        #ELSE?
    # prepare sale ammount
    ammount = {
            "total": str(total),
            "currency": "EUR"
            }
    
    # prepare items for sale
    for item in products:
        items.append({
            "name": item.name,
            "description": item.description,
            "quantity": str(cart_items[str(item.id)]) if current_user.is_anonymous \
                    else str(quantities[item.id]),
            "price": str(item.price),
            "sku": str(item.id),
            "currency": "EUR"
        })
    payment = Payment({
        "intent": "sale",
        "experience_profile_id": web_profile_id(),
        "redirect_urls":
        {
            "return_url": "http://sandbox.paypal.com/execute",
            "cancel_url": "http://sandbox.paypal.com/cancel"
        },
        "payer": {
            "payment_method": "paypal",
        },
        "transactions": [
        {
            "item_list": {
                "items": items, 
            },
            "amount": ammount,
            "description": "This is a guest transaction."
        }]
    })
    
    # Create Payment and return status( True or False )
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Create guest user
        print(payment)
        # Order created
        return jsonify(paymentID=payment.id)
    else:
        # Display Error message
        print("Error while creating payment:")
        print(payment.error)
        #TODO ErrorHandling: Specific -> General 
        flash(payment.error['message'], 'warning')
        response = jsonify(redirect_url=url_for('shop.cart'))
        response.status_code = 302
        return response


@payment.route('/payment/execute', methods=['POST'])
def execute():
    """
    Execute paypal payment
    """
    paymentID = request.form['paymentID']
    payerID = request.form['payerID']
    try:
        payment = Payment.find(paymentID)
    except ResourceNotFound:
        flash('Invalid payment ID', 'warning')
        response = jsonify(redirect_url=url_for('shop.cart'))
        response.status_code = 302
        return response   


    if payment.execute({"payer_id" : payerID}):  # return True or False
        print("Payment[%s] execute successfully" % (payment.id))
        # create guest user 
        if not current_user.is_authenticated:
            guest_name = 'guest_{}'.format(''.join(random.choice(string.ascii_uppercase) for i in range(12)))
            guest = User(
                    username=guest_name,
                    created_at=datetime.utcnow(),
                    user_role='customer',
                    is_registered=False
                    )
            try:
                db.session.add(guest)
                db.session.flush()
                u_id = guest.id
                session['guest'] = guest.id
            except:
                raise #TODO ErrorHandling
        else:
            u_id = current_user.id
        
        # Set initial status
        status = OrderStatus.query.filter_by(name='Processing').first()
        if not status: 
            pass #TODO ErrorHandling
        print(payment)
        try:
            order = Order(
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                payment_id=payment.id,
                user_id=u_id,
                total_ammount=payment.transactions[0].amount.total,
                status_id=status.id
                )

            db.session.add(order)
            db.session.flush()
        except:
            flash('Could not connect to database. Please, try again later', 'warning')
            response = jsonify(redirect_url=url_for('shop.cart'))
            response.status_code = 302
            return response   
        
        items = payment.transactions[0].item_list.items
        order_items = []
        product_updates = []
        for item in items:
            # move cart items to order items
            order_items.append(OrderItem(
                    order_id=order.id,
                    product_id=item.sku,
                    quantity=item.quantity,
                    price=Decimal(item.price)))
            # decrese product count
            product = Product.query.filter_by(id=item.sku).first()
            if not product:
                flash('Sorry, we can\'t find the product you are trying to order!', 'danger')
                response = jsonify(redirect_url=url_for('shop.cart'))
                response.status_code = 302
                return response
            product.quantity -= item.quantity
            if product.quantity < 0:
                flash('One of the products you are trying to order is no longer available!', 'danger')
                response = jsonify(redirect_url=url_for('shop.cart'))
                response.status_code = 302
                return response

            product_updates.append(product)
        try:
            # update order
            db.session.merge(order)
            # add order items
            for item in order_items:
                db.session.add(item)
            # clear cart
            if current_user.is_authenticated:
                cart_items = Cart.query.filter_by(user_id=current_user.id).all()
                for item in cart_items:
                    db.session.delete(item)
            else:
                session['cart'] = {}
            # update product quantities
            for item in product_updates:
                db.session.merge(item) 
            # commit transaction
            db.session.commit()
        except:
            raise #TODO: ErrorHandling
            flash("You can't do this right now. Please, try again later", 'warning')
            response = jsonify(redirect_url=url_for('shop.cart'))
            response.status_code = 302
            return response
        response = jsonify(redirect_url=url_for('customer.order_detail', id=order.id, u_id=order.user_id))
        response.status_code = 302
        flash('You have successfully completed your order', 'info')
        return response

    else:
        print(payment.error)
        flash(payment.error['message'], 'warning')
        #TODO: Error Handling
        response = jsonify(redirect_url=url_for('shop.cart'))
        response.status_code = 302
        return response

@payment.route('/payment/cancel', methods=['GET', 'POST'])
def cancel():
    token = request.args.get('token')
    return ('', 204)


@payment.route('/payment/detail/<string:id>')
def detail(id):
    """
    Get paypal payment detail
    """
    payment_id = id
    print(request)
    try:
        # Retrieve the payment object by calling the
        # `find` method
        # on the Payment class by passing Payment ID
        payment = Payment.find(payment_id)
        print("Got Payment Details for Payment[%s]" % (payment.id))
        items = payment.transactions[0].item_list.items
        shipping_address = payment.transactions[0].item_list.shipping_address
        payer = payment.payer
        ammount = payment.transactions[0].ammount
        if payment.stat == 'approved':
            flash('Your payment has been successful', 'info')
        return render_template('payment/payment.html', items=items, shipping_address=shipping_address, payer=payer, ammount=ammount, title="Payment")

    except ResourceNotFound as error:
        # It will through ResourceNotFound exception if the payment not found
        flash("Payment Not Found", 'danger')
        return redirect(url_for('shop.cart')) 

@payment.route('/payment/refund/<string:id>')
@login_required
def refund(id):
    """
    Refund a paypal identified by paymentID
    """
    if current_user.user_role != 'admin':
        abort(403)
    # only admin can refund
    try:
        payment = Payment.find(id)
    except ResourceNotFound:
        flash("Payment Not Found", 'warning')
        return redirect(url_for('admin.list_orders'))

    sale_id = payment.transactions[0].related_resources[0].sale.id
    print(payment)
    # doing complete refund
    sale_amount = {
            'amount': {
                'currency': payment.transactions[0].related_resources[0].sale.amount.currency,
                'total': payment.transactions[0].related_resources[0].sale.amount.total }
            }
    #del sale_amount['amount']['details']
    print(sale_amount)
    sale = Sale.find(sale_id)
    refund = sale.refund(sale_amount) # refund full ammount
    
    if refund.success():
        flash("Refund[%s] Success" % (refund.id), 'info')
    else:
        flash(refund.error['message'], 'warning')
        print(refund.error)
    return redirect(url_for('admin.list_orders'))
