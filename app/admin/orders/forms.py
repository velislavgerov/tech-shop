from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ...models import OrderStatus

class StatusForm(FlaskForm):
    """
    Form for admin to add or edit a Category.
    """
    choices = [(OrderStatus.SENT, 'Dispatched'),(OrderStatus.RECV, 'Received')]
    status = SelectField('Status', validators=[DataRequired()], choices=choices)
    submit = SubmitField('Submit')
