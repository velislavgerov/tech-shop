from flask import flash, redirect, request, render_template, url_for
from flask_login import current_user, login_required
from paypalrestsdk import Payment, Sale, ResourceNotFound
from sqlalchemy import desc

from .. import admin
from ... import db
from ...models import Order, OrderStatus, OrderItem
from .forms import StatusForm

from datetime import datetime

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.user_role == 'admin':
        abort(403)

def redirect_url(default='shop.index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)
           
@admin.route('/orders', methods=['GET','POST'])
@login_required
def list_orders():
    """
    List all departments
    """
    check_admin()

    orders = Order.query.order_by(desc(Order.updated_at)).all()

    return render_template('admin/orders/orders.html', orders=orders, title="Orders")

@admin.route('/orders/detail/<string:id>', methods=['GET','POST'])
@login_required
def edit_order(id):
    """
    List all departments
    """
    check_admin()

    order = Order.query.filter_by(payment_id=id).first()
    form = StatusForm()
    form.status = order.status
    return render_template('admin/orders/order.html', order=order, form=form, title="Order Detail")

@admin.route('/orders/remove/<int:id>', methods=['GET','POST'])
@login_required
def remove_order(id):
    """
    List all departments
    """
    check_admin()

    order = Order.query.filter_by(id=id).first()
    if not order:
        print("not found")
        flash('Could not find order.')
        return redirect(url_for('admin.list_orders'))
    if order.status.name != 'Pending payment':
        print("pending")
        flash('You can\'t delete this order.')
    else:
        try:
            db.session.delete(order)
            db.session.commit()
            flash('Order deleted.')
        except:
            raise
    return redirect(url_for('admin.list_orders'))

@admin.route('/orders/refund/<int:id>', methods=['GET','POST'])
@login_required
def refund_order(id):
    """
    List all departments
    """
    check_admin()

    order = Order.query.filter_by(id=id).first()
    payment_id = order.payment_id
    
    try:
        payment = Payment.find(payment_id)
    except ResourceNotFound:
        flash("Payment Not Found", "danger")
        return redirect(redirect_url())
    except ServerError:
        flash("There was a problem with PayPal. Please try again later.", "warning")
        return redirect(redirect_url())

    sale_id = payment.transactions[0].related_resources[0].sale.id
    # refund full ammount
    sale_amount = {
            'amount': {
                'currency': payment.transactions[0].related_resources[0].sale.amount.currency,
                'total': payment.transactions[0].related_resources[0].sale.amount.total }
            }

    sale = Sale.find(sale_id)
    refund = sale.refund(sale_amount) # refund full ammount
    
    if refund.success():
        flash("Refund[%s] Success" % (refund.id))
        status = OrderStatus.query.filter_by(name='Refunded').first()
        order.status_id = status.id
        order.cancelled = True
        order.updated_at = datetime.utcnow()
        order_items = OrderItem.query.filter_by(order_id=order.id).all()
        product_items = []
        try:
            for item in order_items:
                product = item.product
                product.quantity += item.quantity
                db.session.merge(item)
            db.session.merge(order)
            db.session.commit()
        except:
            flash('Items counld not be returned to inventory', "warning")

        # XXX: this can fail at any point below. Not good, as refund is registed
    else:
        flash(refund.error['message'], 'warning')
        print(refund.error)
    return redirect(redirect_url())
