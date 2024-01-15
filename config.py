class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'thisisasecretekey'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOGIN_VIEW = 'login'
