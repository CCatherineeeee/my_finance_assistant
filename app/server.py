import os
from os import listdir
from dotenv import load_dotenv
from flask import Flask, render_template, url_for, redirect, jsonify, request
from flask import request
from flask_migrate import Migrate
from flask_login import login_user,LoginManager,current_user,logout_user,login_required
from app import app, db, bcrypt, login_manager
from app.forms import LoginForm, RegisterForm
from app.models import User, BankAccount, Transaction
from datetime import date
from sqlalchemy import func

import plaid
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_get_request import ItemGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest  

    

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
    access_tokens = get_access_token_of_user()
    print ("current access token/s: ", access_tokens)
    balance =  0
    balance += get_account_balance(access_tokens[0])
        
    # get transactionfrom all accounts
    transactions = display_transactions()
    if len(transactions) == 0:
        return render_template('dashboard.html', balance = balance)
    
    # category spendings
    category_spendings = show_transaction_based_on_category()
    return render_template('dashboard.html', balance = balance, transactions = transactions, category_spendings=category_spendings)

@login_required
def get_access_token_of_user():
    bank_accounts = BankAccount.query.filter_by(user_id=current_user.username).all()
    access_tokens = [account.access_token for account in bank_accounts] # in this way, even we only have one accesstoken, it can still well handel 
    return access_tokens
        
def get_account_balance(access_token):
    # print ("get access token: ", access_token)
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)
    accounts = response['accounts']
    balance = 0
    for account in accounts:
        balance += account["balances"]["current"]
    return balance


@app.route('/account_management', methods=['GET', 'POST'])
@login_required
def account_management():
    print ("welcome to account management page, ", current_user.username)
    bank_accounts = BankAccount.query.filter_by(user_id=current_user.username).all()
    return render_template('account_management.html', bank_accounts=bank_accounts)

def get_accounts_from_accesstoken(access_token):
    request = AccountsBalanceGetRequest(access_token=access_token)
    response = client.accounts_balance_get(request)
    accounts = response['accounts']
    balance = 0
    print (accounts)
    for account in accounts:
        balance += get_account_balance(account)
    return balance

    
def get_account_info(account): # helper function for BankAccount Table...?
    account_subtype = account["subtype"]
    account_type = account["type"]
    account_name = account["name"]
    account_official_name = account["official_name"]
    
    
    

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

########################################## Flask Endpoints  ########################################## 

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
    print ("link token:", link_response)
    return jsonify(link_response.to_dict())


@app.route('/server/swap_public_token', methods=['POST'])
def swap_public_token():
    print ("triggered endpoint: swap public token")
    if request.method == 'POST':
        data = request.get_json()
        public_token = data['publicToken']
        print ("backend received public token: ", public_token, "Now run exchangeRequest")
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(exchange_request)
        store_access_token(response)
        return redirect(url_for('dashboard'))
    
@login_required
def store_access_token(exchange_response):
    print ("storing access token to database")
    access_token = exchange_response['access_token']
    item_id = exchange_response['item_id']
    print ("storing access token for current user: ", current_user.username)
    new_bank_account = BankAccount(user_id=current_user.username, access_token=access_token, item_id = item_id)
    db.session.add(new_bank_account)
    db.session.commit()
    
    
    
@app.route('/server/add_transaction_history', methods=['GET'])
def get_transaction_history():
    print ("now adding transaction to database")
    accessTokens = get_access_token_of_user()
    accessToken = accessTokens[0]
    print ("in function, accesstoken: ", accessToken)
    request = TransactionsGetRequest(
            access_token=accessToken,
            start_date=date(1900, 1, 1),
            end_date=date(2025, 12, 25)
    )
    response = client.transactions_get(request)
    
    account_name_dict = {}
    for account in response['accounts']:
        account_id = account["account_id"]
        account_official_name = account["official_name"]
        account_name_dict[account_id] = account_official_name
        
    raw_transactions = response['transactions']
    for transaction in raw_transactions:
        account_id = transaction['account_id']
        category = transaction["personal_finance_category"]["primary"]
        category_icon = transaction["personal_finance_category_icon_url"]
        merchant_name = transaction["merchant_name"]
        logo_url = transaction["logo_url"]
        the_date = str(transaction["date"])
        amount = float(transaction["amount"])
        account_official_name = account_name_dict[account_id]
        new_row = Transaction(account_id = account_id, category=category, category_icon = category_icon, merchant_name =merchant_name, logo_url = logo_url, amount = amount, date = the_date, account_official_name = account_official_name)
        db.session.add(new_row)
    db.session.commit()
    return redirect(url_for('dashboard'))
    
def display_transactions():
    data = Transaction.query.all()
    return data

@app.route('/server/clear_transaction_table')
def clear_transaction_table():
    db.session.query(Transaction).delete()
    db.session.commit()
    return redirect(url_for('dashboard'))
    
    
@app.route('/dashboard/show_transaction_based_on_category') 
def show_transaction_based_on_category():
    category_sums = (
    db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total_spending')
    )
    .group_by(Transaction.category)
    .all()
    )
    categories = []
    spendings = []
    for category, total_spending in category_sums:
        if int(total_spending) > 0:
            categories.append(str(category))
            spendings.append(int(total_spending))
        # print(f"Category: {category}, Total Spending: {total_spending}")
    print ([categories, spendings])
    return [categories, spendings]
    
    
@app.route('/process_user_request', methods=['POST'])    
def process_user_request():
    user_query = request.form.get('user_query')
    
    
    
    
    
    
@app.route('/budget/create_budget')
def create_budget():
    pass

@app.route('/budget/prediction')
def spending_prediction():
    # based on transaction database, predict spending in each category this month
    pass

