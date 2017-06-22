from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

import os

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


class ProductForm(FlaskForm):
    """
    Form for admin to add or edit a product.
    """
    name = StringField('Name', validators=[DataRequired()])
    kind = StringField('Kind', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    image = FileField('Image', validators=[FileAllowed(ALLOWED_EXTENSIONS,
                                'Images only!')])
    submit = SubmitField('Submit')
