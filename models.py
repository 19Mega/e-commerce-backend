from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from main import app

db = SQLAlchemy(app)

class DeliveryState(Enum):
    PENDING = "Pending"
    IN_TRANSIT = "In Transit"
    AT_COMPANY = "At Company"
    DELIVERED = "Delivered"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)
    
    # Relationships: 1 user n Address / Favorite / Cart / Payment / OrderDetail /Order
    address = db.relationship('Address', backref='user', lazy=True)  # <---
    payments = db.relationship('Payment', backref='user', lazy=True)  # <---
    favorites = db.relationship('Favorite', backref='user', lazy=True)  # <---
    cart = db.relationship('Cart', backref='user', lazy=True)  # <---
    order_detail = db.relationship('OrderDetail', backref='user', lazy=True)  # <---
    order = db.relationship('Order', backref='user', lazy=True)  # <---
    
    def __repr__(self):
        return f'<User {self.id}>'

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin
        }

class Address(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name_surname = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(50), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    street = db.Column(db.String(80), nullable=False)
    street_number = db.Column(db.Integer, nullable=False)
    no_number = db.Column(db.Boolean(), default=False)
    references = db.Column(db.String(120), nullable=False)
    
    # Relationships: 1 user n Address
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ---
    
    def __repr__(self):
        return f'<Address {self.id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "name_surname": self.name_surname,
            "phone": self.phone,
            "department": self.department,
            "city": self.city,
            "street": self.street,
            "street_number": self.street_number,
            "no_number": self.no_number,
            "references": self.references,
            "user_id": self.user_id,
        }
        
class Payment(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    card_number = db.Column(db.Integer, nullable=False)
    expiration_date = db.Column(db.String(50), nullable=False)
    #cvv = db.Column(db.Integer, nullable=False)
    
    # Relationships: 1 user n Payment
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ---
    
    def __repr__(self):
        return f'<Payment {self.id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "card_number": self.card_number,
            "expiration_date": self.expiration_date,
            #"cvv": self.cvv
        }
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_description = db.Column(db.String(120), nullable=False)
    long_description = db.Column(db.String(120), nullable=True)
    category = db.Column(db.String(120), nullable=True)
    subcategory = db.Column(db.String(120), nullable=True)
    
    # currency_id = db.Column(db.String(3), nullable=False)
    price = db.Column(db.Float, nullable=False)
    discount = db.Column(db.Integer, nullable=True)
    stock = db.Column(db.Integer, nullable=False)
    
    characteristic_1_title = db.Column(db.String(60), nullable=True)
    characteristic_2_title = db.Column(db.String(60), nullable=True)
    characteristic_3_title = db.Column(db.String(60), nullable=True)
    characteristic_4_title = db.Column(db.String(60), nullable=True)
    
    characteristic_1_description = db.Column(db.String(120), nullable=True)
    characteristic_2_description = db.Column(db.String(120), nullable=True)
    characteristic_3_description = db.Column(db.String(120), nullable=True)
    characteristic_4_description = db.Column(db.String(120), nullable=True)
    
    image_1 = db.Column(db.String(200), nullable=False)
    image_2 = db.Column(db.String(200), nullable=True)
    image_3 = db.Column(db.String(200), nullable=True)
    image_4 = db.Column(db.String(200), nullable=True)
        
    # Relationships: 1 product n Favorite / Cart /
    favorites = db.relationship('Favorite', backref='product', lazy=True)  # <---
    carts = db.relationship('Cart', backref='product', lazy=True)  # <---
    order_detail = db.relationship('OrderDetail', backref='product', lazy=True)  # <---

    
    def __repr__(self):
        return f'<Product {self.id}>'
    
    def serialize_basic(self):
        return{
            "id": self.id,
            "short_description": self.short_description,
            # "currency_id": self.currency_id,
            "price": self.price,
            "discount": self.discount,
            "image_1": self.image_1,
        }
    
    def serialize_full(self):
        return {
            "id": self.id,
            "short_description": self.short_description,
            "long_description": self.long_description,
            "category": self.category,
            "subcategory": self.subcategory,
            # "currency_id": self.currency_id,
            "price": self.price,
            "discount": self.discount,
            "stock": self.stock,
            
            "characteristic_1_title": self.characteristic_1_title,
            "characteristic_2_title": self.characteristic_2_title,
            "characteristic_3_title": self.characteristic_3_title,
            "characteristic_4_title": self.characteristic_4_title,
            "characteristic_1_description": self.characteristic_1_description,
            "characteristic_2_description": self.characteristic_2_description,
            "characteristic_3_description": self.characteristic_3_description,
            "characteristic_4_description": self.characteristic_4_description,
            
            "image_1": self.image_1,
            "image_2": self.image_2,
            "image_3": self.image_3,
            "image_4": self.image_4,
        }
    
    def serialize_cart_item(self) :
        return{
            "id": self.id,
            "short_description": self.short_description,
            # "currency_id": self.currency_id,
            "price": self.price,
            "discount": self.discount,
            "stock": self.stock,
            "image_1": self.image_1,
        }
               
class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Relationships: 1 user n Favorite / Product
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ---
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # ---
    
    def __repr__(self):
        return f'<Favorite {self.id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id
        }
        
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, default=1)
    
    # Relationships: 1 user n Cart / Product
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ---
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # ---
    
    def __repr__(self):
        return f'<Cart {self.id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity
        }
        
class OrderDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
        
    product_name = db.Column(db.String(120), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    product_quantity = db.Column(db.Integer, nullable=False)
    product_category = db.Column(db.String(120), nullable=False)
    product_subcategory = db.Column(db.String(120), nullable=False)
    
    product_offer = db.Column(db.Integer, nullable=True)
        
    product_brand = db.Column(db.String(120), nullable=True)
    product_model = db.Column(db.String(120), nullable=True)
    product_color = db.Column(db.String(120), nullable=True)
    product_size = db.Column(db.String(120), nullable=True)
    product_weight = db.Column(db.Integer, nullable=True)
    
    product_guarantee = db.Column(db.String(120), nullable=True)
    product_guarantee_description = db.Column(db.String(120), nullable=True)
    
    subtotal = db.Column(db.Float, nullable=False)   
    
    # Relationships: 1 user n OrderDetail / Order / Product /
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ---
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)  # ---
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)  # ---
    
    def __repr__(self):
        return f'<Order {self.id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "order_id": self.order_id,
            
            "product_name": self.product_name,
            "product_price": self.product_price,
            "product_quantity": self.product_quantity,
            "product_category": self.product_category,
            "product_subcategory": self.product_subcategory,
            
            "product_offer": self.product_offer,
            "product_brand": self.product_brand,
            "product_model": self.product_model,
            "product_color": self.product_color,
            "product_size": self.product_size,
            "product_weight": self.product_weight,
            
            "product_guarantee": self.product_guarantee,
            "product_guarantee_description": self.product_guarantee_description,
            
            "subtotal": self.subtotal,
        }
            
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    taxes = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    deliver_state = db.Column(db.Enum(DeliveryState), default=DeliveryState.PENDING)

    # Relationships: 1 order n OrderDetail 
    order_details = db.relationship('OrderDetail', backref='order', lazy=True)  # <---
    
    # Relationships: 1 user n Order
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ---
    
    def __repr__(self):
        return f'<Order {self.id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "deliver_state": self.deliver_state,            
            "taxes": self.taxes,            
            "total": self.total,
            "date": self.date
        }
    
class Advertising(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(540), unique=True, nullable=False)
    product_id =  db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<Order {self.id}>'
    
    def serialize(self):
        return {
            "id": self.id,
            "image_url": self.image_url,
            "category": self.category,
        }