from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from ..models import User

class RegistrationForm(FlaskForm):
    """Form for users to create new account."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
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

#class ProfileForm(FlaskForm):

#class AddressForm(FlaskForm):
#    """Form fo user's addresses"""
#    country = db.Column(db.String(50))
#    county = db.Column(db.String(80))
#    city = db.Column(db.String(80))
#    postcode = db.Column(db.String(16))

