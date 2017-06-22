from flask import abort, render_template
from flask_login import current_user, login_required

from ..models import Product

from . import home

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    return render_template('home/index.html', title="Welcome")

@home.route('/shop')
@login_required
def shop():
    """
    Render the dashboard template on the /dashboard route
    """

    products = Product.query.all()

    return render_template('home/shop.html', products=products, title="Shop")

@home.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """
    Render the admin dashboard template on the /admin/dashboard route
    """
    # prevent non-admins from accessing the page
    if not current_user.is_admin:
        abort(403)

    return render_template('home/admin_dashboard.html', title="Dashboard")
