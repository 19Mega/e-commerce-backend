import json
from main import app, db
from models import User 

from flask import request, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

bcrypt = Bcrypt()

# -----

@app.route('/create_table')
def create_table():
    db.create_all()
    return "Tabla creada!"

@app.route('/insert_user')
def insert_user():
    
    new_user = User(name="Juan")
    db.session.add(new_user)
    db.session.commit()
    return "Usuario insertado!"

@app.route('/delete_table')
def delete_table():
    db.drop_all()
    return "Tabla eliminada!"

# -----


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
    
    if user.is_admin:
        return jsonify(access_token= access_token, 
                user_id= user.id,
                user_name = user.name,
                user_email = user.email,
                user_admin = user.is_admin 
                ), 200

    return jsonify(access_token= access_token, 
                    user_id= user.id,
                    user_name = user.name,
                    user_email = user.email,
                    ), 200
