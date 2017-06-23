from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextField, SubmitField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from ...models import Category

def enabled_categories():
    return Category.query.all()

class CategoryForm(FlaskForm):
    """
    Form for admin to add or edit a Category.
    """
    name = StringField('Name', validators=[DataRequired()])
    description = TextField('Description', validators=[DataRequired()],
                                            widget=TextArea())
    submit = SubmitField('Submit')

class SubcategoryForm(FlaskForm):
    """
    Form for admin to add or edit a Subcategory.
    """
    category = QuerySelectField('Category', query_factory=enabled_categories, allow_blank=True) 
    name = StringField('Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Submit')
