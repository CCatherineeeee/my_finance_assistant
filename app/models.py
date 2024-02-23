from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, login_manager

# create User table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True, name='constraint_name_unique')
    password = db.Column(db.String(80), nullable=False, name='constraint_name_nullable') # because we don't know how long it will be after hashing, so make it 80 here
    bank_accounts = db.relationship('BankAccount', backref='user', lazy=True)
    
class BankAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    access_token = db.Column(db.String(100))
    item_id = db.Column(db.String(100))


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.String(255))
    category = db.Column(db.String(255))
    category_icon = db.Column(db.String(255))
    merchant_name = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    amount = db.Column(db.Float)
    date = db.Column(db.String(10))
    account_official_name = db.Column(db.String(255))
    
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))