# app/__init__.py
from flask import Flask
from flask_login import LoginManager
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)

from app import server, models

# Create database tables
with app.app_context():
    db.create_all()
