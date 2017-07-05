from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

from .. import admin
from .forms import ProductForm
from ... import db
from ...models import Product, Category

from os.path import join, dirname, relpath
from os import remove
from datetime import datetime


def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.user_role == 'admin':
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
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(join('app/static/uploads/',filename))
        else:
            filename = None
        product = Product(category_id=form.category.data.id,
                            name=form.name.data,
                            description=form.description.data,
                            main_image=filename,
                            price=form.price.data,
                            quantity=form.quantity.data,
                            added_by=current_user.email,
                            added_at=datetime.utcnow(),
                            updated_by=current_user.email,
                            updated_at=datetime.utcnow()
                            )
        try:
            # add product to the database
            db.session.add(product)
            db.session.commit()
            # XXX: raw save might not be a good idea! (overwrite?)
            flash('You have successfully added a new product', 'info')
        except IntegrityError: # relies on unique name in the database!
            raise
            flash('Error: product name already exists.', 'warning')
        except:
            raise # XXX: app will fail if we can't save the image
        
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
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(join('app/static/uploads/',filename))
            product.main_image = filename
        else:
            filename = None
        # TODO: Should delete old one or have a better way to manage images
        product.name = form.name.data
        product.category_id=form.category.data.id,
        product.description=form.description.data,
        product.price=form.price.data,
        product.quantity=form.quantity.data,
        product.updated_by=current_user.email,
        product.updated_at=datetime.utcnow()
        db.session.commit()
        flash('You have successfully edited the product.', 'info')

        # redirect to the departments page
        return redirect(url_for('admin.list_products'))

    form.name.data = product.name
    form.category.data = Category.query.filter(Category.id==product.category_id).one()
    form.price.data = product.price
    form.quantity.data = product.quantity
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
    
    # delete image file
    try:
       remove(join('app/static/uploads/', product.image))
    except:
        pass #XXX: We should know about this

    flash('You have successfully deleted the product.', 'info')

    # redirect to the products page
    return redirect(url_for('admin.list_products'))
    
    return render_template(title="Delete Department")
