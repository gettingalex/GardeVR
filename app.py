import sqlite3
from flask import Flask, jsonify, render_template, request, redirect
import os
import stripe

app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect('bookings.db')

domain_url = "http://127.0.0.1:5000/"

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
}
stripe.api_key = stripe_keys["secret_key"]

@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/checkout')
def checkout():
    print("Checkout page")
    return render_template("checkout.html")

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            ui_mode = 'embedded',
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1Oe8GaLTe1GzTq0NzT4ydxJO',
                    'quantity': 1,
                },
            ],
            mode='payment',
            return_url=domain_url + '/return.html?session_id={CHECKOUT_SESSION_ID}',
            automatic_tax={'enabled': True},
        )
    except Exception as e:
        return str(e)

    return jsonify(clientSecret=session.client_secret)


@app.route('/session-status', methods=['GET'])
def session_status():
  session = stripe.checkout.Session.retrieve(request.args.get('session_id'))

  return jsonify(status=session.status, customer_email=session.customer_details.email)

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
