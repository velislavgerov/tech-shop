from flask import abort, render_template, request
from flask_login import current_user, login_required

from ..models import Product, Category

from . import home

@home.route('/')
def homepage():
    """
    Render the homepage template on the / route
    """
    search = request.args.get('search')
    category = request.args.get('category')
    categories = Category.query.all()
    if search:
        products = Product.query.filter(Product.name.like('%{}%'.format(search))).all()
    else:
        products = Product.query.all()
    if category:
        try:
            c_id = Category.query.filter_by(name = category).one()
            products = Product.query.filter_by(category_id = c_id.id).all()
        except:
            raise
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
