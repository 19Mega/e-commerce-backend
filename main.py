from flask import Flask, jsonify
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify({"Choo Choo": f"Welcome to your Flask app 🚅{os.getenv('TEST')}"})

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
