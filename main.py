import os
import pymysql

from flask import Flask, jsonify
from dotenv import load_dotenv, find_dotenv
from flask_sqlalchemy import SQLAlchemy

from datetime import timedelta 
from flask_jwt_extended import JWTManager

load_dotenv(find_dotenv())

# To SQLAlchemy use PyMySQL
pymysql.install_as_MySQLdb()

app = Flask(__name__)

app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

db_user = os.getenv('MYSQLUSER')
db_password = os.getenv('MYSQLPASSWORD')
db_host = os.getenv('MYSQLHOST')
db_port = os.getenv('MYSQLPORT')
db_name = os.getenv('MYSQLDATABASE')

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///default.db' # To run it localy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from routes import *

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
