from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
#from wtforms.file import FileField, FileAllowed, FileRequired

class ProductForm(FlaskForm):
    """
    Form for admin to add or edit a product.
    """
    name = StringField('Name', validators=[DataRequired()])
    kind = StringField('Kind', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    #upload = FileField('image',
    #                    validators=[FileRequired(),
    #                        FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])
    submit = SubmitField('Submit')
