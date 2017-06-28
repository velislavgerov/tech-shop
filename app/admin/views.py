from flask import flash, abort, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user

from . import admin
from ..customer.forms import LoginForm, RegistrationForm, AccountForm

from .. import db
from ..models import User, Order

from datetime import datetime

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    try:
        if not current_user.is_admin:
            abort(403)
    except AttributeError:
        # customer's dont' have is_admin property
        abort(403)

@admin.route('/')
@login_required
def dashboard():
    """
    Render the admin dashboard template on the /admin/dashboard route
    """
    print(current_user)
    check_admin()

    return render_template('admin/admin_dashboard.html', title="Dashboard")


@admin.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    """
    Handle requests to the /register route
    Add a registered user to the database through the registration form
    """
    
    check_admin()

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data,
                    is_admin=True,
                    created_at=datetime.utcnow())
        
        # add user to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.')

        # redirect to the login page
        return redirect(url_for('admin.dashboard'))

    # load registration template
    return render_template('customer/register.html', form=form, title='Register')

@admin.route('/login', methods=['GET', 'POST'])
def login():
    """Handle requests to the /login route
    Log an employee in through the login form
    """
    
    form = LoginForm()
    if form.validate_on_submit():
        # check weather user exists in the database and wherther
        # the password entered matches the password in the database
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(
                form.password.data):
            print(user)
            login_user(user)
            return redirect(url_for('admin.dashboard')) 
        # when login details are incorrect
        else:
            flash('Invalid email or password.')
    # load login template
    return render_template('customer/login.html', form=form, titile='Login')

@admin.route('/logout')
@login_required
def logout():
    """Handle request to the /logout route
    Log a user out thorugh the logout link
    """
    check_admin()

    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('admin.login'))
