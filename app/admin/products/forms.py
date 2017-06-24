from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextField, DecimalField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea, Input, FileInput
from wtforms.ext.sqlalchemy.fields import QuerySelectField

import os

from ...models import Category, Supplier

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def enabled_categories():
    return Category.query.all()

def enabled_suppliers():
    return Supplier.query.all()

class ProductForm(FlaskForm):
    """
    Form for admin to add or edit a product.
    """
    name = StringField('Name', validators=[DataRequired()])
    description = TextField('Description', validators=[DataRequired()], widget=TextArea())
    price = DecimalField('Price', places=2, validators=[DataRequired('Please enter a valid price.')])
    quantity = IntegerField('Quantity',validators=[DataRequired()], widget=Input('number'))
    image = FileField('Image File', 
                    validators=[FileAllowed(ALLOWED_EXTENSIONS,'Images only!')])
    category = QuerySelectField('Category',validators=[DataRequired()], query_factory=enabled_categories, get_label='name', allow_blank=True) 
    supplier = QuerySelectField('Supplier', query_factory=enabled_suppliers, get_label='name', allow_blank=True)
    submit = SubmitField('Submit')
