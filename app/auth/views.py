from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user

from . import auth
from .forms import LoginForm, RegistrationForm, AccountForm

from .. import db
from ..models import User, Address, OrderDetail

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handle requests to the /register route
    Add a user to the database through the registration form
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    password=form.password.data)
        
        # add user to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.')

        # redirect to the login page
        return redirect(url_for('auth.login'))

    # load registration template
    return render_template('auth/register.html', form=form, title='Register')

@auth.route('/account', methods=['GET','POST'])
@login_required
def account():
    """
    Handles requests to the user account page
    """
    form = AccountForm()
    address = Address.query.filter_by(user_id=current_user.id).first()
    if form.validate_on_submit():
        if not address:
            address = Address(user_id=current_user.id)
        address.tel_number = form.tel_number.data
        address.address_line_1 = form.address_line_1.data
        address.address_line_2 = form.address_line_2.data
        address.city = form.city.data
        address.county = form.county.data
        address.postcode = form.postcode.data
        address.country = form.country.data
        try:
            db.session.merge(address)
            db.session.commit()
            flash('You have succesfully updated your details.')
        except:
            flash('Sorry, you can\'t do this right now.')
    
    form.email.data = current_user.email
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    if address:
        form.tel_number.data = address.tel_number
        form.address_line_1.data = address.address_line_1
        form.address_line_2.data = address.address_line_2
        form.city.data = address.city
        form.county.data = address.county
        form.postcode.data = address.postcode
        form.country.data = address.country

    return render_template('auth/account.html', form=form, title='Account')

@auth.route('/orders')
@login_required
def orders():
    """
    List all departments
    """

    orders = OrderDetail.query.all()

    return render_template('auth/orders.html', orders=orders, title="Orders")


@auth.route('/login', methods=['GET', 'POST'])
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
            # log user in
            login_user(user)
            
            # redirect to the the appropriate dashboard page
            if user.is_admin:
                return redirect(url_for('home.admin_dashboard'))
            else:
                return redirect(url_for('home.homepage'))

        # when login details are incorrect
        else:
            flash('Invalid email or password.')
    # load login template
    return render_template('auth/login.html', form=form, titile='Login')

@auth.route('/logout')
@login_required
def logout():
    """Handle request to the /logout route
    Log a user out thorugh the logout link
    """
    logout_user()
    flash('You have successfully been logged out.')

    # redirect to the login page
    return redirect(url_for('auth.login'))
