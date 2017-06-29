from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import PasswordField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo

from ..models import User

## May use in future, if we are to hold phone number values
#def validate_phone(form, field):
#    if len(field.data) > 16:
#        raise ValidationError('Invalid phone number.')
#    try:
#        input_number = phonenumbers.parse(field.data)
#        if not (phonenumbers.is_valid_number(input_number)):
#            raise ValidationError('Invalid phone number.')
#    except:
#        input_number = phonenumbers.parse("+1"+field.data)
#        if not (phonenumbers.is_valid_number(input_number)):
#            raise ValidationError('Invalid phone number.')


class RegistrationForm(FlaskForm):
    """Form for users to create new account."""
    username = StringField('Username', validators=[DataRequired()])
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

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First name', render_kw={'readonly': True})
    last_name = StringField('Last name', render_kw={'readonly': True}) 
    submit = SubmitField('Update')
