from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import datetime
from utils.sqalchemy import DictModel
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__,static_folder='/uploads')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@127.0.0.1/specterr'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Users(db.Model, DictModel):
    id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    token = db.Column(db.String(255), nullable=True)
    no_logins = db.Column(db.Integer,nullable=True, default=0)