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
import logging


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.secret_key = os.environ["app_secret_key"]  # replace with your actual secret key


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
    id = db.Column(db.Integer, primary_key=True)
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
        query = text(f'SELECT * FROM "{table}"')
        result = db.session.execute(query)
        print(result)
        data = [row._asdict() for row in result]
        tables_data[table] = data
    return render_template('db_dashboard.html', tables=tables_data)

@app.route('/termes')
def termes():
    product_id = request.args.get('product_id')
    price_id = request.args.get('price_id')
    quantity = request.args.get('quantity')

    return render_template('termes.html', product_id=product_id, price_id=price_id, quantity=quantity)


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
            invoice_creation={"enabled": True},
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
    logging.info('received webhook')
    product_id_checkout = []

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the webook 
    if event['type'] == 'payment_intent.succeeded' or event['type'] == 'charge.succeeded' or event['type'] == 'payment_intent.created' or event['type'] == 'checkout.session.completed':
        print('found event type')
        logging.info('found event type')
        session_metadata = event['data']['object']['metadata']
        if session_metadata:
            session_product_id = event['data']['object']['metadata']['product_id']
            product_id_checkout.append(session_product_id)
            print("Product_id:" + session_product_id)
            logging.info("Product_id:" + session_product_id)
            print("product_id_checkout:" + str(product_id_checkout[0]))
            logging.info("product_id_checkout:" + str(product_id_checkout[0]))

            session_address = event['data']['object']['customer_details']['address']
            session_email = event['data']['object']['customer_details']['email']
            session_name = event['data']['object']['customer_details']['name']

            handle_checkout_session(product_id_checkout, session_address, session_email, session_name)
            
        else:
            print("No metadata")
            logging.info('No metadata')
            # Then define and call a method to handle the successful checkout
            # Fulfill the purchase...
            # handle_checkout_session(session_product_id)
        # Then define and call a method to handle the successful checkout

        # Fulfill the purchase...
        #if product_id_checkout:
        #    handle_checkout_session(product_id_checkout)
    

    else:
        print('Unhandled event type {}'.format(event['type']))
        logging.info('Unhandled event type {}'.format(event['type']))

    return 'success' ##jsonify(success=True)


def handle_checkout_session(product_id_checkout, session_address, session_email, session_name):
    print("Payment was successful in handle checkout.")
    logging.info("Payment was successful in handle checkout.")
    # Assuming the product id is stored in session
    product_id = str(product_id_checkout[0])
    print("product_id in handle checkout: " + product_id)
    address = f"{session_address['line1']}, {session_address['line2']}, {session_address['city']}, {session_address['state']}, {session_address['country']}, {session_address['postal_code']}"
    print('user address in handle checkout: ' + address)
    update_stock(product_id, address, session_email, session_name)

def update_stock(product_id, address, email, name):
    logging.info('prep to update stock')
    print('prep to update stock')
    # Get the product from the database
    product = Product.query.filter_by(id=product_id).first()
    #logging.info('product for DB:'+ str(product))
    #logging.info('product_id from webhook' + product_id)
    #print('product for DB:'+ str(product))
    #print('product_id from webhook' + product_id)

    # Decrease the stock by 1
    product.stock_quantity -= 1
    logging.info('stock reduced by 1')
    print('stock reduced by 1')

    # Create user
    # Check if user with the given address and name already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user is None:
        # Create a new user
        new_user = User(name=name, firstname="", lastname="", email=email, address=address)
        db.session.add(new_user)
        db.session.commit()
        logging.info('New user added to the database')
        print('New user added to the database')
    
    # Create a new order
    user_id = existing_user.id if existing_user else new_user.id
    new_order = Order(user_id=user_id, product_id=product_id, order_date=datetime.utcnow())
    db.session.add(new_order)

    # Commit the changes
    db.session.commit()
    #logging.info('db changed commited')
    print('db changed commited')

@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/cancelled")
def cancelled():
    return render_template("cancelled.html")

#End of Stripe API

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(host="0.0.0.0", debug=False, port=10000)
