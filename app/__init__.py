import flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

import os

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

try:
    app.config['SECRET_KEY'] = os.environ['FLASK_SECRET_KEY']
except KeyError:
    print('Please set a FLASK_SECRET_KEY environment variable.')
    raise SystemExit

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

from . import routes
