#code reference https://testdriven.io/blog/flask-stripe-tutorial/ with repo https://github.com/testdrivenio/flask-stripe-checkout

import os
from flask import Flask, jsonify, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import stripe
from flask_migrate import Migrate
import time

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.secret_key = '101010'  # replace with your actual secret key




# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)
domain_url = "http://127.0.0.1:5000/"

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
    "endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"]
}
stripe.api_key = stripe_keys["secret_key"]

#DB Model Setup
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.firstname}>'
    
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False) 
    price = db.Column(db.Integer, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    price_id = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'
    
#End of DB setup


@app.route('/')
def index():
    products = Product.query.all()
    return render_template("index.html", products=products)

#Stripe API
@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)

@app.route('/process_variable', methods=['GET', 'POST'])
def process_variable():
    data = request.get_json()
    session['price'] = data['product_price']  # assign the received value to 'price'
    # Now you can use 'price' in your application
    return 'Success!', 200

# Can add recurring payment with  https://stripe.com/docs/recurring-payments#installment-plans
@app.route("/create-installment-session")
def create_installment_session():
    stripe.api_key = stripe_keys["secret_key"]
    price = session.get('price')  # retrieve price from session
    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means x6                                                                                                                                                                                                                                                                     the redirect will have the session ID set as a query param
        checkout_session = stripe.SubscriptionSchedule.create(
            customer='{{CUSTOMER_ID}}',
            start_date="now",
            end_behavior="cancel",
            phases=[
                {
                "items": [
                    {
                    "price_data": {
                        "currency": "usd",
                        "product": "prod_PT4R8sMVH9bImH",
                        "recurring": {"interval": "month"},
                        "unit_amount": 774,
                    },
                    "quantity": 1,
                    },
                ],
                "iterations": 6,
                },
            ],
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route("/create-checkout-session")
def create_checkout_session():
    stripe.api_key = stripe_keys["secret_key"]
    price = session.get('price')  # retrieve price from session
    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means x6                                                                                                                                                                                                                                                                     the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            expires_at=int(time.time() + (3600 * 2)), # Configured to expire after 2 hours
            line_items=[
                {
                    "price": price,
                    "quantity": 1
                }
            ]
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403



@app.route("/webhook", methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        session = event['data']['object']

        # Fulfill the purchase...
        handle_checkout_session(session)

    return 'Success', 200


def handle_checkout_session(session):
    print("Payment was successful.")
    # TODO: run some custom code here

@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/cancelled")
def cancelled():
    return render_template("cancelled.html")

#End of Stripe API

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
