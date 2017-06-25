from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager

from enum import Enum

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
    #addresses = db.relationship('Address')
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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) # remove pk for multiple addresses
    tel_number = db.Column(db.Text, nullable=False)
    address_line_1 = db.Column(db.Text, nullable=False)
    address_line_2 =  db.Column(db.Text)
    city = db.Column(db.String(80), nullable=False)
    county = db.Column(db.String(80), nullable=False)
    postcode = db.Column(db.String(16), nullable=False)
    country = db.Column(db.String(50), nullable=False)
            

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
    images = db.relationship('Image')
    carts = db.relationship('Cart')

class Supplier(db.Model):
    """Create a Supplier table"""
    # XXX: What about distributors?

    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    main_image = db.Column(db.Integer, db.ForeignKey('images.id'))
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    website_url = db.Column(db.Text)


class Category(db.Model):
    """Create a Category table."""
    
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)

class Subategory(db.Model):
    """Create a Subategory table."""
    
    __tablename__ = 'subcategories'

    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    name = db.Column(db.String(80), index=True, unique=True, nullable=False)
    description = db.Column(db.Text(), nullable=False)

class Image(db.Model):
    """Create an Image table."""

    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    filename = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)

class Cart(db.Model):
    """Create a Cart table."""

    __tablename__ = 'carts'
    __table_args__ = ( db.UniqueConstraint('user_id', 'product_id'), { } )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

class OrderStatus(Enum):
    """Enum type to hold order statuses"""
    RECV = "Order created"
    PAID = "Payment confirmed"
    DISP = "Dispatching"
    SENT = "Delivering"
    DLVD = "Delivered"

class UserOrders(db.Model):
    """Create an UserOrders table."""
    
    __tablename__ = 'users_orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    order_id = db.Column(db.Integer, db.ForeignKey('orders_detail.id'))

class OrderDetail(db.Model):
    """Create an OrderDetail table."""
   
    __tablename__ = 'orders_detail'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True)
    first_name = db.Column(db.String(60), index=True)
    last_name = db.Column(db.String(60), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    tel_number = db.Column(db.Text, nullable=False)
    address_line_1 = db.Column(db.Text, nullable=False)
    address_line_2 =  db.Column(db.Text)
    city = db.Column(db.String(80), nullable=False)
    county = db.Column(db.String(80), nullable=False)
    postcode = db.Column(db.String(16), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime(), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.RECV)
    payment_id = db.Column(db.Text, index=True, unique=True, nullable=False)

class OrderItem(db.Model):
    """Create an OrderItem table."""

    __tablename__ = 'orders_items'
    __table_args__ = ( db.UniqueConstraint('user_id', 'product_id', 'order_id'), { } )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders_detail.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)



