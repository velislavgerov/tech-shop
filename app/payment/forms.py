from flask_wtf import FlaskForm, RecaptchaField, Recaptcha
from wtforms import StringField, TextField, SubmitField, ValidationError
from wtforms.validators import DataRequired
from wtforms.fields.html5 import TelField
from wtforms.widgets import TextArea

from ..models import OrderDetail

class OrderDetailForm(FlaskForm):
    """Form for customer orders."""
    email = StringField('Email', validators=[DataRequired()], render_kw={'readonly': True})
    first_name = StringField('First name',validators=[DataRequired()], render_kw={'readonly': True})
    last_name = StringField('Last name', validators=[DataRequired()], render_kw={'readonly': True})
    tel_number = TelField('Phone number', validators=[DataRequired()])
    address_line_1 = StringField('Address Line 1', validators=[DataRequired()])
    address_line_2 = StringField('Address Line 2 (optional)')
    city = StringField('Town/City', validators=[DataRequired()])
    county = StringField('County', validators=[DataRequired()])
    postcode = StringField('Postcode', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    message = TextField('Message', widget=TextArea())
    #recaptcha = RecaptchaField(validators=[Recaptcha('Are you a bot or a human?')])
    submit = SubmitField('Confirm')


