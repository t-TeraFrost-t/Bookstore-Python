import os
from flask import Flask, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from datetime import timedelta
from flask_mail import Mail
from flask_bcrypt import Bcrypt
import flask_excel as excel
from psycogreen.gevent import patch_psycopg

patch_psycopg()  # the only change


app = Flask(__name__, template_folder='views')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://hlanyiegpohmkh:8f5051602023d1893cfa28dcb25ec5f8875682740a6b68a458fff5a950c70e21@ec2-99-80-170-190.eu-west-1.compute.amazonaws.com:5432/divqiaop85jk0'
app.config['SECRET_KEY'] = '7d32da10cecc362833c07714408b63bc'
db = SQLAlchemy(app)
engine = create_async_engine('postgresql+asyncpg://mincho:PALEsedem@localhost/testbookstore')
async_session = sessionmaker( engine, expire_on_commit=True, class_=AsyncSession)
app.permanent_session_lifetime = timedelta(hours=1)
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'angelsedmakov@gmail.com'
app.config['MAIL_PASSWORD'] = 'PALEsedem'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['WTF_CSRF_METHODS'] = []
mail = Mail(app)
bcrypt = Bcrypt(app)
excel.init_excel(app)

from bookstore import routs
