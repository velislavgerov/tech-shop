from flask import request, url_for
from flask_login import current_user

def check_admin():
    """
    Prevent non-admins from accessing the page
    """
    if not current_user.user_role == 'admin':
        abort(403)

def redirect_url(default='shop.index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

