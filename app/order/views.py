from flask import request, jsonify, abort, flash, render_template, request, url_for, redirect, session
from flask_login import current_user, login_required
from paypalrestsdk import Payment, WebProfile, Sale, ResourceNotFound

from . import order

from ..models import Product, Category, Cart, Order, OrderItem, OrderStatus, User
from .. import db

from datetime import datetime
import random, string
from decimal import Decimal

@order.route('/orders')
@login_required
def orders():
    """
    List all orders
    """
    if not current_user.user_role == 'admin': 
        orders = Order.query.filter_by(user_id=current_user.id).all()
        return render_template('customer/orders.html', orders=orders, title="Orders")
    else:
        orders = Order.query.all()
        return render_template('admin/orders/orders.html', orders=orders, title="Orders")


@order.route('/orders/<int:id>', defaults={'u_id': None}, methods=['GET', 'POST'])
@order.route('/orders/<int:id>/<int:u_id>', methods=['GET', 'POST'])
def order_detail(id, u_id):
    """
    List all details for order by id
    """
    if not u_id and current_user.is_authenticated:
        u_id = current_user.id

    order = Order.query.filter_by(id=id, user_id=u_id).first()

    # - guest orders are publically visible
    # - user orders are visible only to them
    if not order \
        or (current_user.is_authenticated and order.user.id != current_user.id\
        and not current_user.user_role == 'admin')\
        or (not current_user.is_authenticated and order.user.is_registered):
        flash('Order not found.', 'info')
        if current_user.is_authenticated:
            return redirect(url_for('customer.orders'))
        else:
            return redirect(url_for('shop.index'))
    
    try:
        # Retrieve the payment object by calling the
        # `find` method
        # on the Payment class by passing Payment ID
        payment = Payment.find(order.payment_id)
        print("Got Payment Details for Payment[%s]" % (payment.id))
        #items = payment.transactions[0].item_list.items
        shipping_address = payment.transactions[0].item_list.shipping_address
        shipping_address.phone = payment.payer.payer_info.phone
        #payer = payment.payer
        payment_state = payment.transactions[0].related_resources[0].sale.state 
        # admin only
        form = None
        if current_user.is_authenticated and current_user.user_role == 'admin':
            form = StatusForm()
            if form.validate_on_submit():
                order.status = form.status.data
                order.updated_at = datetime.utcnow()
                try:
                    db.session.merge(order)
                    db.session.commit()
                except:
                    flash('You can\'t do this right now.', 'warning')
                
                return render_template('customer/order.html', order=order, payment_state=payment_state,eshipping_address=shipping_address, form=form, title="Order Details")

            form.status.data = order.status 

        return render_template('customer/order.html', order=order, payment_state=payment_state, shipping_address=shipping_address, form=form, title="Order Details")

    except ResourceNotFound as error:
        # It will through ResourceNotFound exception if the payment not found
        # Hm?
        flash("Payment Not Found", 'danger')
        return redirect(url_for('shop.index'))
    
    except ConnectionError as error:
        flash('There was a problem with contacting PayPal. Please try again later', 'warning')
        return redirect(url_for('shop.index'))




