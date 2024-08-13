from flask import Flask, jsonify
import os
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy

load_dotenv(find_dotenv())

app = Flask(__name__)

db_user = os.getenv('MYSQLUSER')
db_password = os.getenv('MYSQLPASSWORD')
db_host = os.getenv('MYSQLHOST')
db_port = os.getenv('MYSQLPORT')
db_name = os.getenv('MYSQLDATABASE')

# app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('MYSQL_URL', 'sqlite:///default.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def index():
    return jsonify({"Choo Choo": f"Welcome to your Flask app 🚅{os.getenv('TEST', 'No test value')}"})


db = SQLAlchemy(app)

from routes import *

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
