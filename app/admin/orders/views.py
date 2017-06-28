from flask import render_template
from flask_login import current_user, login_required

from .. import admin
from ... import db
from ...models import Order
from .forms import StatusForm

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
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
