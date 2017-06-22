from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from . import admin
from .forms import ProductForm
from .. import db
from ..models import Product, Image

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

# Product views

@admin.route('/products', methods=['GET','POST'])
@login_required
def list_products():
    """
    List all departments
    """
    check_admin()

    products = Product.query.all()

    return render_template('admin/products/inventory.html', products=products, title="Inventory")

@admin.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """
    Add a product to the database
    """
    check_admin()

    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data,
                            kind=form.kind.data,
                            description=form.description.data)
        try:
            # add product to the database
            db.session.add(product)
            db.session.commit()
            flash('You have successfully added a new product')
        except:
            # in case product already exists
            # TODO: catch diff errors
            flash('Error: product name already exists.')

        # redirect to products page
        return redirect(url_for('admin.list_products'))
    # load products template
    return render_template('admin/products/product.html', action='Add',
            add_product=add_product, form=form, title='Add Department')


@admin.route('/products/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_product(id):
    """
    Edit a product
    """
    check_admin()

    add_product = False

    product = Product.query.get_or_404(id)
    form = ProductForm(obj=product)
    if form.validate_on_submit():
        product.name = form.name.data
        product.kind = form.kind.data
        product.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the product.')

        # redirect to the departments page
        return redirect(url_for('admin.list_products'))

    form.name.data = product.name
    form.kind.data = product.kind
    form.description.data = product.description
    return render_template('admin/products/product.html', action="Edit",
                           add_product=add_product, form=form,
                           product=product, title="Edit Product")

@admin.route('/products/delete/<int:id>', methods=['GET','POST'])
@login_required
def delete_product(id):
    """
    Delete a product from the database
    """
    check_admin()

    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    flash('You have successfully deleted the product.')

    # redirect to the products page
    return redirect(url_for('admin.list_products'))
    
    return render_template(title="Delete Department")
