from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo
from wtforms.fields.html5 import TelField

from ..models import User

class RegistrationForm(FlaskForm):
    """Form for users to create new account."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[
                                        DataRequired(),
                                        EqualTo('confirm_password')
                                        ])
    confirm_password = PasswordField('Confirm Password')
    recaptcha = RecaptchaField(validators=[Recaptcha('Are you a bot or a human?')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email is already in use.')

class LoginForm(FlaskForm):
    """Form for users to login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class AccountForm(FlaskForm):
    """Form for users to edit their account."""
    email = StringField('Email', render_kw={'readonly': True})
    first_name = StringField('First name', render_kw={'readonly': True})
    last_name = StringField('Last name', render_kw={'readonly': True})
    tel_number = TelField('Phone number')
    address_line_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line_2 = StringField('Address Line 2 (optional)')
    city = StringField('Town/City', validators=[DataRequired()])
    county = StringField('County', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    recaptcha = RecaptchaField(validators=[Recaptcha('Are you a bot or a human?')])
    submit = SubmitField('Update')


#class AddressForm(FlaskForm):
#    """Form fo user's addresses"""
#    country = db.Column(db.String(50))
#    county = db.Column(db.String(80))
#    city = db.Column(db.String(80))
#    postcode = db.Column(db.String(16))

