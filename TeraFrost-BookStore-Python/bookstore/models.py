from bookstore import db
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Payment(db.Model):
    __tablename__ = 'payments'
    id =  db.Column('id', db.Unicode, primary_key=True, unique = True, nullable=False)
    time_of_creation = db.Column('time_of_creation',db.Date,nullable=False)
    id_status = db.Column('id_status', db.Integer, nullable=False)
    payment_types = db.Column(db.Integer,db.ForeignKey('payment_types.id') , nullable=False)
    
class TypeOfPayment(db.Model):
    __tablename__ = 'payment_types'
    id =  db.Column('id', db.Integer, primary_key=True, unique = True, nullable=False)
    name = db.Column('name', db.Unicode, nullable=False)
    payments = db.relationship('Payment',backref='type',lazy=True)
    __mapper_args__ = {"eager_defaults": True}

class StatusOfOrder(db.Model):
    __tablename__ = 'status_of_order'
    id =  db.Column('id', db.Integer, primary_key=True, unique = True, nullable=False)
    name = db.Column('name', db.Unicode, nullable=False)
    orders = db.relationship('Order',backref='status',lazy=True)
    __mapper_args__ = {"eager_defaults": True}


class Currency(db.Model):
    __tablename__ = 'currency'
    id =  db.Column('id', db.Integer, primary_key=True, unique = True, nullable=False)
    name = db.Column('name', db.Unicode, nullable=False)
    books = db.relationship('Book',backref='currency',lazy=True)
    books_in_order = db.relationship('BooksInOrder',backref='currency',lazy=True)
    orders = db.relationship('Order',backref='currency',lazy=True)
    __mapper_args__ = {"eager_defaults": True}

class Gener(db.Model):
    __tablename__ = 'geners'
    id =  db.Column('id', db.Integer, primary_key=True, unique = True, nullable=False)
    name = db.Column('name', db.Unicode, nullable=False)
    books = db.relationship('Book',backref='gener',lazy=True)
    __mapper_args__ = {"eager_defaults": True}

class Book(db.Model):
    __tablename__ = 'books'
    isbn = db.Column('isbn', db.Unicode, primary_key=True, unique = True, nullable=False)
    id =  db.Column('id', db.Integer, unique = True, nullable=False)
    name = db.Column('name', db.Unicode, nullable=False)
    autor = db.Column('autor', db.Unicode, nullable=False)
    price = db.Column('price', db.Integer, nullable=False)
    cover = db.Column('cover', db.Unicode, nullable=False)
    amount = db.Column('amount', db.Integer, nullable=False)
    description = db.Column('description', db.Unicode, nullable=False)
    discount = db.Column('discount', db.Unicode, nullable=False)
    id_gener = db.Column(db.Integer,db.ForeignKey('geners.id'))
    id_currency = db.Column(db.Integer,db.ForeignKey('currency.id'))
    books_in_basket = db.relationship("BooksInBasket",backref='book',lazy=True)
    books_in_order = db.relationship("BooksInOrder",backref='book',lazy=True)
    __mapper_args__ = {"eager_defaults": True}

class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column('id',db.Integer,primary_key=True, unique = True, nullable=False)
    name = db.Column('username', db.Unicode,  unique = True,nullable=False)
    email = db.Column('email', db.Unicode,  unique = True,nullable=False)
    password = db.Column('password', db.Unicode,  unique = True,nullable=False)
    salt = db.Column('salt', db.Unicode,  unique = True,nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column('id',db.Integer,primary_key=True, unique = True, nullable=False)
    username = db.Column('username', db.Unicode,  unique = True,nullable=False)
    email = db.Column('email', db.Unicode,  unique = True,nullable=False)
    password = db.Column('password', db.Unicode,  unique = True,nullable=False)
    salt = db.Column('salt', db.Unicode,  unique = True,nullable=False)
    basket = db.relationship('Basket',backref='user',lazy=True)
    orders = db.relationship('Order',backref='user',lazy=True)

class Basket(db.Model):
    __tablename__ = 'baskets'
    id = db.Column('id',db.Integer,primary_key=True, unique = True, nullable=False)
    creation_date = db.Column('creation_date',db.Date,nullable=False)
    id_user = db.Column(db.Integer,db.ForeignKey('users.id'))
    books_in_basket = db.relationship("BooksInBasket",backref='basket',lazy=True)
class BooksInBasket(db.Model):
    __tablename__ = 'books_in_basket'
    id = db.Column('id',db.Integer,primary_key=True, unique = True, nullable=False)
    id_basket = db.Column(db.Integer,db.ForeignKey('baskets.id'))
    id_book = db.Column(db.Integer,db.ForeignKey('books.id'))
    number_of_books = db.Column('number_of_books', db.Integer, nullable=False)

class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column('id',db.Integer,primary_key=True, unique = True, nullable=False)
    creation_date = db.Column('creation_date',db.Date,nullable=False)
    id_user = db.Column(db.Integer,db.ForeignKey('users.id'))
    price = db.Column('price', db.Integer, nullable=False) 
    books_in_order = db.relationship("BooksInOrder",backref='order',lazy=True)
    id_payment = db.Column(db.Unicode,db.ForeignKey('payments.id'), nullable=True)
    id_status = db.Column(db.Integer,db.ForeignKey('status_of_order.id'))
    id_currency = db.Column(db.Integer,db.ForeignKey('currency.id'))
class BooksInOrder(db.Model):
    __tablename__ = 'books_in_order'
    id = db.Column('id',db.Integer,primary_key=True, unique = True, nullable=False)
    id_order = db.Column(db.Integer,db.ForeignKey('orders.id'))
    id_book = db.Column(db.Integer,db.ForeignKey('books.id'))
    number_of_books = db.Column('number_of_books', db.Integer, nullable=False)
    current_price = db.Column('current_price', db.Integer, nullable=False) 
    id_currency = db.Column(db.Integer,db.ForeignKey('currency.id'))

