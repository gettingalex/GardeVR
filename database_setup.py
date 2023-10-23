import sqlite3

# Connect to the database file
conn = sqlite3.connect('bookings.db')

# Create a table for user profiles
conn.execute('''CREATE TABLE users
             (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             email TEXT NOT NULL,
             phone TEXT NOT NULL,
             password TEXT NOT NULL);''')

# Create a table for the first product
conn.execute('''CREATE TABLE 20feet
             (product_id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             description TEXT NOT NULL,
             price REAL NOT NULL);''')

# Create a table for the second product
conn.execute('''CREATE TABLE 35feet
             (product_id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             description TEXT NOT NULL,
             price REAL NOT NULL);''')

# Create a table for bookings
conn.execute('''CREATE TABLE bookings
             (booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id INTEGER NOT NULL,
             product_id INTEGER NOT NULL,
             date TEXT NOT NULL,
             time TEXT NOT NULL,
             FOREIGN KEY (user_id) REFERENCES users(user_id),
             FOREIGN KEY (product_id) REFERENCES product1(product_id),
             FOREIGN KEY (product_id) REFERENCES product2(product_id));''')

# Commit the changes and close the connection
conn.commit()
conn.close()
