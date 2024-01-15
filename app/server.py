from flask import Flask, render_template, url_for, redirect
from flask_migrate import Migrate
from flask_login import login_user,LoginManager,current_user,logout_user,login_required
from app import app, db, bcrypt
from app.forms import LoginForm, RegisterForm
from app.models import User

# app = Flask(__name__)
# bcrypt = Bcrypt(app)
# app.config['SQLALCHEMY_DATABASE_URI'] = '' # connect server to database
# app.config['SECRET_KEY'] = 'thisisasecretekey'
# db = SQLAlchemy(app)

    
# login_manager = LoginManager()
# login_manager.session_protection = "strong"
# login_manager.login_view = "login"
# login_manager.login_message_category = "info"
# db = SQLAlchemy()
# migrate = Migrate()
# bcrypt = Bcrypt()
    
# def create_app():
#     app = Flask(__name__)

#     app.secret_key = 'secret-key'
#     app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#     app.config['SECRET_KEY'] = 'thisisasecretekey'

#     login_manager.init_app(app)
#     db.init_app(app)
#     migrate.init_app(app, db)
#     bcrypt.init_app(app)
    
#     return app
    
    

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
        
    
    return render_template('register.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route('/register', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))