from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, login_manager

# create User table
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True, name='constraint_name_unique')
    password = db.Column(db.String(80), nullable=False, name='constraint_name_nullable') # because we don't know how long it will be after hashing, so make it 80 here
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))