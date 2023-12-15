from flask import Flask, jsonify
import json
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token
import os
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myapp.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://db_wyuf_user:Q0oBcLIpwajVcrywOOLd6UN8cqUOAJRu@dpg-clloj01fb9qs73938cpg-a.oregon-postgres.render.com/db_wyuf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["JWT_SECRET_KEY"] = app.config.get("JWT_SECRET_KEY", "default_secret_key")
app.json_encoder = json.JSONEncoder
jwt = JWTManager(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from myapp.models import User, Category, Record

import myapp.views

