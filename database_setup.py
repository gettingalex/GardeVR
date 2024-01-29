from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    password = Column(String)

class Product(Base):
    __tablename__ = 'Products'

    product_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    price = Column(Float)
    stock_quantity = Column(Integer)
    type = Column(String)

class Booking(Base):
    __tablename__ = 'bookings'

    booking_id = Column(Integer, primary_key=True)
    user_id = Column(Integer)

# User Model
class User(Base):
    # ... other fields ...
    user_id = Column(Integer, primary_key=True)
    bookings = relationship('Booking', backref='user', lazy=True)

#Booking-User Model
class Booking(Base):
    # ... other fields ...
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)

# Product Model
class Product(Base):
    # ... other fields ...
    bookings = relationship('Booking', backref='product', lazy=True)

# Booking-Product Model
class Booking(Base):
    # ... other fields ...
    product_id = Column(Integer, ForeignKey('product.product_id'), nullable=False)

# Create the database
engine = create_engine('sqlite:///bookings.db')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()