import sqlite3
from flask import Flask

app = Flask(__name__)

# Connect to the SQLite database
conn = sqlite3.connect('bookings.db')

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
