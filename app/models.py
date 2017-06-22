from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

class User(UserMixin, db.Model):
    """Crete a User table."""

    # Ensures that the table will be named in plural
    __tablename__  = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    addresses = db.relationship('Address')
    carts = db.relationship('Cart')

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
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {} {}'.format(self.first_name, self.last_name)

    # Set up user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

class Address(db.Model):
    """Create an Address table."""

    __tablename__ = 'addresses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    country = db.Column(db.String(50))
    county = db.Column(db.String(80))
    city = db.Column(db.String(80))
    postcode = db.Column(db.String(16))

class Product(db.Model):
    """Create a Product table."""
    
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    kind = db.Column(db.String(80), index=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    image = db.Column(db.String(80))
    images = db.relationship('Image')
    carts = db.relationship('Cart')

class Image(db.Model):
    """Create an Image table."""

    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    url = db.Column(db.Text, nullable=False)
    is_main = db.Column(db.Boolean, default=False) # possibly bad design

class Cart(db.Model):
    """Create a Cart table."""

    __tablename__ = 'carts'
    __table_args__ = ( db.UniqueConstraint('user_id', 'product_id'), { } )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

# TODO:
#class Order(db.Model):
#    """Create an Order table."""
#    pass
