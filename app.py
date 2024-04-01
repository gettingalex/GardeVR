#code reference https://testdriven.io/blog/flask-stripe-tutorial/ with repo https://github.com/testdrivenio/flask-stripe-checkout

from sqlalchemy import inspect
import os
from flask import Flask, jsonify, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import stripe
from flask_migrate import Migrate
import time
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import text


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.secret_key = '101010'  # replace with your actual secret key

auth = HTTPBasicAuth()

USER_DATA = {
    "admin": generate_password_hash("admin")
}

# Configure the SQLAlchemy part of the app instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookings.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)
migrate = Migrate(app, db)
domain_url = "https://gardevr.onrender.com" #http://127.0.0.1:5000

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
    id = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False) 
    price = db.Column(db.Integer, nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False)
    price_id = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'<Product {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    product_id = db.Column(db.String(100), db.ForeignKey('product.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))
    
    def __repr__(self):
        return f'<Order {self.id}>'
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

#DB dashboard auth
@auth.verify_password
def verify_password(username, password):
    if username in USER_DATA and \
            check_password_hash(USER_DATA.get(username), password):
        return username


@app.route('/db_dashboard')
@auth.login_required
def db_dashboard():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    tables_data = {}
    for table in tables:
        data = db.session.query(db.Model).from_statement(text(f"SELECT * FROM {table}")).all()
        tables_data[table] = [str(item) for item in data]
    return render_template('db_dashboard.html', tables=tables_data)


@app.route('/process_variable', methods=['GET', 'POST'])
def process_variable():
    data = request.get_json()
    session['price'] = data['product_price']  # assign the received value to 'price'
    session['product_id'] = data['product_ID'] # assign the received product id
    # Now you can use 'price' in your application
    return 'Success!', 200

@app.route("/create-checkout-session")
def create_checkout_session():
    stripe.api_key = stripe_keys["secret_key"]
    price = session.get('price')  # retrieve price from session
    product_id = session.get('product_id') #retrieve product_id from session
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
            success_url=domain_url + "/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "/cancelled",
            payment_method_types=["card"],
            metadata={"product_id":product_id},
            billing_address_collection="required",
            automatic_tax={"enabled": True},
            #tax_behavior="exclusive",
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
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']
    print(payload)
    print("received webhook")
    product_id_checkout = []

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )
        print("listening for event")

    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the webook 
    if event['type'] == 'payment_intent.succeeded' or event['type'] == 'charge.succeeded' or event['type'] == 'payment_intent.created' or event['type'] == 'checkout.session.completed':
        print('payment intent succeeded')
        session_metadata = event['data']['object']['metadata']
        if session_metadata:
            session_product_id = event['data']['object']['metadata']['product_id']
            product_id_checkout.append(session_product_id)
            print("Product_id:" + session_product_id)
            print("product_id_checkout:" + str(product_id_checkout[0]))
            handle_checkout_session(product_id_checkout)
            
        else:
            print("No metadata")
            # Then define and call a method to handle the successful checkout
            # Fulfill the purchase...
            # handle_checkout_session(session_product_id)
        # Then define and call a method to handle the successful checkout

        # Fulfill the purchase...
        #if product_id_checkout:
        #    handle_checkout_session(product_id_checkout)
    

    else:
        print('Unhandled event type {}'.format(event['type']))

    return 'success' ##jsonify(success=True)


def handle_checkout_session(product_id_checkout):
    print("Payment was successful in handle checkout.")
    # Assuming the product id is stored in session
    product_id = str(product_id_checkout[0])
    ("product_id in handle checkout: " + product_id)
    #update_stock(product_id)

def update_stock(product_id):
    print('prep to update stock')
    # Get the product from the database
    product = Product.query.filter_by(product_id=product_id).first()
    print('product for DB:'+ product)
    print('product_id from webhook' + product_id)

    # Decrease the stock by 1
    #product.stock -= 1

    # Commit the changes
    #db.session.commit()

@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/cancelled")
def cancelled():
    return render_template("cancelled.html")

#End of Stripe API

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host="0.0.0.0", debug=True, port=10000)
