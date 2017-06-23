from flask import Blueprint

admin = Blueprint('admin', __name__)

from .products import views
from .categories import views
