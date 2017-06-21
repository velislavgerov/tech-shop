from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class User(UserMixin, db.Model):
    """Crete an User table."""

    # Ensures that the table will be named in plural
    __tablename__  = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        """Prevent password from beign accessed"""
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """Hash an set password."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if password matches actual password"""
        return check_password_hash(password)

    def __repr__(self):
        return '<User: {} {}'.format(self.first_name, self.last_name)

    # Set up user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

