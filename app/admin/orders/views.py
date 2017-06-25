from flask import render_template
from flask_login import current_user, login_required

from .. import admin
from ... import db
from ...models import OrderDetail

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

    orders = OrderDetail.query.all()

    return render_template('admin/orders/orders.html', orders=orders, title="Orders")
