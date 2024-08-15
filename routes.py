import json

from main import app, db
from models import User, Address, Payment , Product, Favorite, Cart, Order, OrderDetail, Advertising
from flask import request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, get_csrf_token, jwt_required, get_jwt_identity

bcrypt = Bcrypt()

# -----

@app.route('/')
def index():
    return jsonify({"Choo Choo": f"Welcome to your Flask app"})

@app.route('/create_table')
def create_table():
    db.create_all()
    return "Tabla creada!"

@app.route('/insert_user')
def insert_user():
    
    new_user = User(name="Juan", email="juan@gmail.com")
    db.session.add(new_user)
    db.session.commit()
    return "Usuario insertado!"

@app.route('/delete_table')
def delete_table():
    db.drop_all()
    return "Tabla eliminada!"

# -----

# -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
# User : CREATE, READ, UPDATE, DELETE

@app.route('/signup', methods=['POST'])
def signup_user():
    body = json.loads(request.data)

    # user exist?
    user = User.query.filter_by(email=body["email"]).first()
    if user is None:  
        # hashing the password
        hashed_password = bcrypt.generate_password_hash(body["password"]).decode('utf-8')

        new_user = User(
            name = body["name"],
            email = body["email"],
            password = hashed_password,
            is_active = body["is_active"],
            is_admin = True,
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created."}), 200
    
    return jsonify({"msg": "User already exists."}), 400

@app.route('/login', methods=['POST'])  
def login_user():
    body = json.loads(request.data)
    email = body["email"]
    password = body["password"]
    
    # user exist?
    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password): #check hashed password
        return jsonify({'msg': 'Invalid username/password'}), 401

    access_token = create_access_token(identity= user.id)
    
    favorites = Favorite.query.filter(Favorite.user_id == user.id).all()      
    user_favorites = [favorite.serialize()['product_id'] for favorite in favorites]
        
    cart = Cart.query.filter(Cart.user_id == user.id).all()
    user_cart = [{"id": cart.product_id, "quantity": cart.quantity} for cart in cart]
    print(user_cart)
    print(access_token)

    if user.is_admin:
        return jsonify(access_token= access_token, 
                user_id= user.id,
                user_name = user.name,
                user_email = user.email,
                user_favorites = user_favorites,
                user_cart = user_cart,
                user_admin = user.is_admin 
                ), 200

    return jsonify(access_token= access_token, 
                    user_id= user.id,
                    user_name = user.name,
                    user_email = user.email,
                    user_favorites = user_favorites,
                    user_cart = user_cart   
                    ), 200

@app.route('/user/<int:user_id>/verify', methods=['GET'])
@jwt_required()
def veify_admin_token(user_id): 
    # verify user
    current_user_id = get_jwt_identity()
    if current_user_id == user_id:
        user = User.query.filter_by(id=user_id).first()
        if user.is_admin: 
            return jsonify(user_admin = user.is_admin), 200
    
    return jsonify({"msg": "Unauthorized."}), 401
   

