from flask import abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError

from .. import admin
from .forms import CategoryForm, SubcategoryForm
from ... import db
from ...models import Category

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.user_role == 'admin':
        abort(403)

@admin.route('/categories', methods=['GET','POST'])
@login_required
def list_categories():
    """
    List all departments
    """
    check_admin()

    categories = Category.query.all()

    return render_template('admin/categories/categories.html', categories=categories, title="Categories")

@admin.route('/category/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """
    Add a category to the database
    """
    check_admin()

    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data,
                            description=form.description.data) 
        try:
            db.session.add(category)
            db.session.commit()
            flash('You have successfully added a new category')
        except IntegrityError: # relies on unique name in the database!
            flash('Error: category name already exists.')

        # redirect to products page
        return redirect(url_for('admin.list_categories'))
    # load products template
    return render_template('admin/categories/category.html', action='Add',
            add_category=add_category, form=form, title='Add Category')


@admin.route('/category/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_category(id):
    """
    Edit a category
    """
    check_admin()

    add_category = False

    category = Category.query.get_or_404(id)
    form = CategoryForm(obj=category)
    if form.validate_on_submit():  
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('You have successfully edited the category.')

        # redirect to the departments page
        return redirect(url_for('admin.list_categories'))

    form.name.data = category.name
    form.description.data = category.description
    return render_template('admin/categories/category.html', action="Edit",
                           add_category=add_category, form=form,
                           category=category, title="Edit Category")

@admin.route('/category/delete/<int:id>', methods=['GET','POST'])
@login_required
def delete_category(id):
    """
    Delete a category from the database
    """
    check_admin()

    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()

    flash('You have successfully deleted the category.')

    return redirect(url_for('admin.list_categories'))

    return render_template(title="Delete Department")
