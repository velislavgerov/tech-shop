from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from paypalrestsdk import Payment, Sale, ResourceNotFound

from .. import admin
from ... import db
from ...models import Order, OrderStatus, OrderItem
from .forms import StatusForm

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.user_role == 'admin':
        abort(403)

@admin.route('/orders', methods=['GET','POST'])
@login_required
def list_orders():
    """
    List all departments
    """
    check_admin()

    orders = Order.query.all()

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
        flash("Payment Not Found")
        return redirect(url_for('admin.list_orders'))

    sale_id = payment.transactions[0].related_resources[0].sale.id
    print(payment)
    # doing complete refund
    sale_amount = {
            'amount': {
                'currency': payment.transactions[0].related_resources[0].sale.amount.currency,
                'total': payment.transactions[0].related_resources[0].sale.amount.total }
            }
    print(sale_amount)
    sale = Sale.find(sale_id)
    refund = sale.refund(sale_amount) # refund full ammount
    
    if refund.success():
        flash("Refund[%s] Success" % (refund.id))
        status = OrderStatus.query.filter_by(name='Refunded').first()
        order.status_id = status.id
        # release items
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
            flash('Items counld not be returned to inventory')
    else:
        flash("Unable to refund")
        flash(refund.error)
    return redirect(url_for('admin.list_orders'))
