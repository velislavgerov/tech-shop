from flask import flash, abort, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user

from sqlalchemy_continuum import changeset, version_class, transaction_class


from . import admin
from ..customer.forms import LoginForm, RegistrationForm, AccountForm

from .. import db
from ..models import User, Order, Activity

from datetime import datetime
import timeago

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.user_role == 'admin':
        abort(403)

@admin.route('/')
@login_required
def dashboard():
    """
    Render the admin dashboard template on the /admin/dashboard route
    """
    activities = Activity.query.order_by(Activity.id.desc()).all()
    for activity in activities:
        date = datetime.utcnow()
        activity.timeago = (timeago.format(activity.transaction.issued_at, date))
    return render_template('admin/admin_dashboard.html', activities=activities, title="Dashboard")


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
                    user_role='admin',
                    is_registered=True,
                    created_at=datetime.now())
        
        # add user to the database
        db.session.add(user)
        db.session.commit()
        flash('You have successfully registered! You may now login.')

        # redirect to the login page
        return redirect(url_for('admin.dashboard'))

    # load registration template
    return render_template('customer/register.html', form=form, title='Register')
