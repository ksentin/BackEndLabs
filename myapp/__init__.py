from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myapp.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_wyuf_user:Q0oBcLIpwajVcrywOOLd6UN8cqUOAJRu@dpg-clloj01fb9qs73938cpg-a.oregon-postgres.render.com/db_wyuf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from myapp.models import User, Category, Record

import myapp.views

jwt = JWTManager(app)