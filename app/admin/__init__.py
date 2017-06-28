from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import views
from .products import views
from .categories import views
from .orders import views

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.is_admin:
        abort(403)

