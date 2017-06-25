from flask import request, jsonify, abort, flash, render_template, request, url_for, redirect
from flask_login import current_user, login_required
from paypalrestsdk import Payment

from . import payment

from ..models import Product, Category, Cart, Address, OrderDetail, OrderItem, OrderStatus
from .. import db

from datetime import datetime

@payment.route('/payment/create', methods=['POST'])
def create():
    """
    Create paypal payment
    """
    if current_user.is_authenticated:
        address = Address.query.filter_by(user_id=current_user.id).first()    
        if address:
            shipping_address= {
                    "recipient_name": "{} {}".format(current_user.first_name,
                                                    current_user.last_name),
                    "line1": address.address_line_1,
                    "line2": address.address_line_2,
                    "city": address.city,
                    "phone": address.tel_number,
                    "country_code": 'GB',
                    "postal_code": address.postcode,
                    "state": address.county
                }
            # create order 
        else:
            response = jsonify(redirect_url=url_for('auth.account'))
            response.status_code = 302
            flash('You should update your account\'s address before you try to order')
            return response
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        quantities = {x.product_id: x.quantity for x in cart_items}
        products = Product.query.filter(Product.id.in_(list(quantities.keys()))).all()
        total = None
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
    # Payment
    # A Payment Resource; create one using
    # the above types and intent as 'sale'
    payment = Payment({
        "intent": "sale",
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
                "shipping_address": shipping_address 
            },
            # Amount
            # Let's you specify a payment amount.
            "amount": ammount,
            "description": "This is the payment transaction description."}
        ]})
    print(payment)
    # Create Payment and return status( True or False )
    if payment.create():
        print("Payment[%s] created successfully" % (payment.id))
        order = OrderDetail(
                email=current_user.email,
                first_name=current_user.first_name,
                last_name=current_user.last_name,
                user_id=current_user.id,
                tel_number=address.tel_number,
                address_line_1=address.address_line_1,
                address_line_2=address.address_line_2,
                city=address.city,
                postcode=address.postcode,
                county=address.county,
                country=address.country,
                created_at=datetime.utcnow(),
                payment_id=payment.id
                )
        try:
            db.session.add(order)
            db.session.commit()
        except:
            return jsonify()

        return jsonify(paymentID=payment.id)
    else:
        # Display Error message
        print("Error while creating payment:")
        print(payment.error)
        flash('Sorry, you can\'t pay right now. Please try again.')
        return jsonify()

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
        #address = payment.transactions[0].item_list.shipping_address
        #phone = payment.transactions[0].item_list.shipping_phone_number
        
        # find corresponding order and change it's status
        order = OrderDetail.query.filter_by(payment_id=paymentID).first()
        order.status = OrderStatus.PAID
        if not order: 
            return('', 500)
        
        # get all cart items
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        order_items = []
        product_updates = []
        for item in cart_items:
            # move cart items to order items
            order_items.append(OrderItem(
                    order_id=order.id,
                    user_id=current_user.id,
                    product_id=item.product_id,
                    quantity=item.quantity))
            # decrese product count
            product = Product.query.filter_by(id=item.product_id).first()
            if not product:
                return('', 500)
            product.quantity -= item.quantity
            if product.quantity < 0:
                return('', 500)
            product_updates.append(product)

        try:
            db.session.merge(order)
            for item in order_items:
                db.session.add(item)
            for item in cart_items:
                db.session.delete(item)
            for item in product_updates:
                db.session.merge(item)
            db.session.commit()
        except:
            return('', 500)
        response = jsonify(redirect_url=url_for('auth.orders'))
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

