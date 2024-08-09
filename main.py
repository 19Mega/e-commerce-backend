from flask import Flask, jsonify
import os
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


load_dotenv(find_dotenv())

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_URL', 'sqlite:///default.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql://{os.environ.get('MYSQLUSER')}:{os.environ.get('MYSQLPASSWORD')}@{os.environ.get('MYSQLHOST')}:{os.environ.get('MYSQLPORT')}/{os.environ.get('MYSQLDATABASE')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'default-secret')

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
