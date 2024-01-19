import os
from os import listdir
from dotenv import load_dotenv
from flask import Flask, render_template, url_for, redirect, jsonify, request
from flask import request
from flask_migrate import Migrate
from flask_login import login_user,LoginManager,current_user,logout_user,login_required
from app import app, db, bcrypt
from app.forms import LoginForm, RegisterForm
from app.models import User

import plaid
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest

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

# refer: https://medium.com/swlh/test-story-635a6c1cfdfd
def compile_javascript():
    # Defining the path to the folder where the JS files are saved
    path = 'app/static/js'
    # Getting all the files from that folder
    files = [f for f in listdir(path) if os.path.isfile(os.path.join(path, f))]
    # Setting an iterator
    i = 0
    # Looping through the files in the first folder
    for file in files:
        # Building a file name
        file_name = "js/" + file
        # Creating a URL and saving it to a list
        all_js_files = []
        all_js_files.append(url_for('static', filename = file_name)) 
        # Updating list index before moving on to next file
        return(all_js_files)
    
    

@app.route('/')
def home():
    all_js_files = compile_javascript()
    print (all_js_files)
    return render_template('home.html', js_files = all_js_files)

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


######### Flask Endpoints

# create plaid client
load_dotenv()

client_id = os.getenv('client_id')
secret = os.getenv('secret')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox') ## why specifying sandbox??

config = plaid.Configuration(
    host = plaid.Environment.Sandbox,
    api_key={
        'clientId': client_id, 
        'secret': secret, 
        }
)
api_client = plaid.ApiClient(config)
client = plaid_api.PlaidApi(api_client)
# client = Client(client_id=client_id, secret=secret, environment='sandbox')

@app.route('/server/create_link_token', methods=['GET', 'POST'])
def generate_link_token():
    # Account filtering isn't required here, but sometimes 
    # it's helpful to see an example. 
    print("triggered endpoint: generate link token")
    link_request = LinkTokenCreateRequest( # not sure of these two, aka if i should call this way or import something
        user= LinkTokenCreateRequestUser(
            client_user_id= "1", # todo: change this user id to primary key in database
        ),
        client_name='My Finance Assistant',
        products=[Products("auth"), Products("transactions")],
        country_codes=[CountryCode("US")],
        language='en',
        webhook='https://sample-web-hook.com',
    )
    # create link token
    link_response = client.link_token_create(link_request)
    #link_token = response['link_token']
    print ("link token:", link_response)
    return jsonify(link_response.to_dict())


@app.route('/server/swap_public_token', methods=['POST'])
def swap_public_token():
    print ("triggered endpoint: swap public token")
    # print (request)
    if request.method == 'POST':
        data = request.get_json()
        public_token = data['publicToken']
        print ("backend received public token: ", public_token, "Now run exchangeRequest")
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)
        access_token = response['access_token']
        item_id = response['item_id']
        print (access_token, item_id)
        return redirect
    
    
    # user_good
    # pass_good
