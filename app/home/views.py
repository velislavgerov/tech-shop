from flask import abort, render_template
from flask_login import current_user, login_required

from ..models import Product, Category

from . import home

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """

    categories = Category.query.all()
    products = Product.query.all()
    print(categories)
    return render_template('home/index.html', categories=categories, products=products, title="Welcome")

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
