from flask import Flask, jsonify
import os
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


load_dotenv(find_dotenv())

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQLHOST', 'sqlite:///default.db')

@app.route('/')
def index():
    return jsonify({"Choo Choo": f"Welcome to your Flask app 🚅{os.getenv('TEST', 'No test value')}"})


jwt = JWTManager(app)
db = SQLAlchemy(app)

from routes import *

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
