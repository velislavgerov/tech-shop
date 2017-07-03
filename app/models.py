from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

from enum import Enum

class User(UserMixin, db.Model):
    """Crete a User table."""

    # Ensures that the table will be named in plural
    __tablename__  = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, index=True)
    first_name = db.Column(db.Text, index=True)
    last_name = db.Column(db.Text, index=True)
    email = db.Column(db.Text, index=True, unique=True)
    password_hash = db.Column(db.String(128))
    user_role = db.Column(db.Text, nullable=False)
    is_registered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(), nullable=False)


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
        return '<User: {} {}>'.format(self.first_name, self.last_name)

    # Set up user_loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

class Product(db.Model):
    """Create a Product table."""
    
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    main_image = db.Column(db.String(80))
    price = db.Column(db.Numeric(10,2), index=True, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    added_by = db.Column(db.String(80), nullable=False)
    added_at = db.Column(db.Date(), nullable=False)
    # last updates
    updated_by = db.Column(db.String(80), nullable=False)
    updated_at = db.Column(db.Date(), nullable=False)

class Supplier(db.Model):
    """Create a Supplier table"""

    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    website_url = db.Column(db.Text)


class Category(db.Model):
    """Create a Category table."""
    
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)

class Subcategory(db.Model):
    """Create a Subategory table."""
    
    __tablename__ = 'subcategories'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)

class Cart(db.Model):
    """Create a Cart table."""

    __tablename__ = 'carts'
    __table_args__ = ( db.UniqueConstraint('user_id', 'product_id'), { } )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

class OrderStatus(db.Model):
    """Create a table to hold our order statuses"""
    
    __tablename__ = 'order_statuses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    description = db.Column(db.Text)

class Order(db.Model):
    """Create a table to hold our orders"""

    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status_id = db.Column(db.Integer, db.ForeignKey('order_statuses.id'))
    payment_id = db.Column(db.Text, unique=True, nullable=False)
    payment_token = db.Column(db.Text)
    #sale_id = db.Column(db.Text, unique=True)
    total_ammount = db.Column(db.Numeric(10,2), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False)
    updated_at = db.Column(db.DateTime(), nullable=False)
    note = db.Column(db.Text)
    status = db.relationship("OrderStatus", backref="parents")
    user = db.relationship("User", backref="parents")
    items = db.relationship("OrderItem", backref="parents")

class OrderItem(db.Model):
    """Create an OrderItem table."""

    __tablename__ = 'orders_items'
    __table_args__ = ( db.UniqueConstraint('product_id', 'order_id'), { } )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    price = db.Column(db.Numeric(10,2), nullable=False)
    product = db.relationship("Product", backref="parents")
