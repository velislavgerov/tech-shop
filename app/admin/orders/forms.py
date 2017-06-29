from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ...models import OrderStatus


def enabled_statuses():
    return OrderStatus.query.all()

class StatusForm(FlaskForm):
    """
    Form for admin to add or edit a Category.
    """
    status = QuerySelectField('Status', query_factory=enabled_statuses, get_label='name', allow_blank=False) 
    submit = SubmitField('Update')


