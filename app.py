import sqlite3
from flask import Flask, jsonify
import os
import stripe

app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect('bookings.db')

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
}

stripe.api_key = stripe_keys["secret_key"]

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
