from flask import request, jsonify, abort, flash, render_template, request, url_for, redirect, session
from flask_login import current_user, login_required
from paypalrestsdk import Payment, WebProfile, ResourceNotFound

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
    total = None
    if current_user.is_authenticated:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        quantities = {x.product_id: x.quantity for x in cart_items}
        products = Product.query.filter(Product.id.in_(list(quantities.keys()))).all()
        if products:
            total = sum([x.price*quantities[x.id] for x in products])
        ammount = {
                "total": str(total),
                "currency": "EUR"
                }
        items = []
        for item in products:
            items.append({
                        "name": item.name,
                        "description": item.description,
                        "quantity": str(quantities[item.id]),
                        "price": str(item.price),
                        "sku": str(item.id),
                        "currency": "EUR"
                        })
    else:
        # Generate PayPal transactions data from the guest cart
        # Specifically, we currently use items and ammount
        cart_items = session['cart']
        products = Product.query.filter(Product.id.in_(list(cart_items.keys()))).all()
        if products:
            total = sum([x.price*cart_items[str(x.id)] for x in products])
        ammount = {
                "total": str(total),
                "currency": "EUR"
                }
        items = []
        for item in products:
            items.append({
                        "name": item.name,
                        "description": item.description,
                        "quantity": str(cart_items[str(item.id)]),
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
        # Payer
        # A resource representing a Payer that funds a payment
        # Use the List of `FundingInstrument` and the Payment Method
        # as 'credit_card'
        "payer": {
            "payment_method": "paypal",
        },
        "transactions": [
        {
            # ItemList
            "item_list": {
                "items": items, 
            },
            "amount": ammount,
            "description": "This is a guest transaction."
        }
    ]
        })
    
    # Create Payment and return status( True or False )
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        # Create guest user
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
            except:
                raise #TODO ErrorHandling
        else:
            u_id = current_user.id
        
        # Set initial status
        status = OrderStatus.query.filter_by(name='Pending payment').first()
        if not status: 
            pass #TODO ErrorHandling
        order = Order(
                created_at=datetime.utcnow(),
                payment_id=payment.id,
                user_id=u_id,
                total_ammount=total,
                status_id=status.id
                )
        try:
            db.session.add(order)
            db.session.commit()
        except:
            raise #TODO ErrorHandling
            return jsonify()
        
        # Order created
        return jsonify(paymentID=payment.id)
    else:
        # Display Error message
        print("Error while creating payment:")
        print(payment.error)
        #TODO ErrorHandling: Specific -> General 
        flash('Sorry, you can\'t pay right now. Please try again.')
        return jsonify(error='payment failed')

@payment.route('/payment/execute', methods=['POST'])
def execute():
    """
    Execute paypal payment
    """
    paymentID = request.form['paymentID']
    payerID = request.form['payerID']
    payment = Payment.find(paymentID)

    if payment.execute({"payer_id" : payerID}):  # return True or False
        print("Payment[%s] execute successfully" % (payment.id))
        # find corresponding order and change it's status
        order = Order.query.filter_by(payment_id=paymentID).first()
        if not order:
            pass #TODO ErrorHandling
        status = OrderStatus.query.filter_by(name='Processing').first()
        if not status: 
            pass #TODO ErrorHandling
        order.status_id = status.id        
        
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
                return('', 500) #TODO: Change all of these
            product.quantity -= item.quantity
            if product.quantity < 0:
                return('', 500)
            product_updates.append(product)
        try:
            db.session.merge(order)
            for item in order_items:
                db.session.add(item)
            if current_user.is_authenticated:
                cart_items = Cart.query.filter_by(user_id=current_user.id).all()
                for item in cart_items:
                    db.session.delete(item)
            else:
                session['cart'] = {}
            for item in product_updates:
                db.session.merge(item) 
            db.session.commit()
        except:
            raise
            return('', 500)
        response = jsonify(redirect_url=url_for('customer.orders'))
        response.status_code = 302
        flash('You have completed your order.')
        return response

    else:
        print(payment.error)
    return ('', 500)

@payment.route('/payment/cancel', methods=['GET', 'POST'])
def cancel():
    token = request.args.get('token')
    return ('', 204)


@payment.route('/payment/detail', methods=['POST'])
def detail():
    """
    Get paypal payment detail
    """
    payment_id = request.form['paymentID']
    print(request)
    try:
        # Retrieve the payment object by calling the
        # `find` method
        # on the Payment class by passing Payment ID
        payment = Payment.find(payment_id)
        print("Got Payment Details for Payment[%s]" % (payment.id))
        print(payment)
        return jsonify(str(payment))

    except ResourceNotFound as error:
        # It will through ResourceNotFound exception if the payment not found
        print("Payment Not Found")

