import os

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# from pymongo.mongo_client import MongoClient
# from pymongo.server_api import ServerApi

load_dotenv()

# uri = os.getenv("MONGO_URI")
# mongo_client = MongoClient(uri, server_api=ServerApi("1"))
# mongo_db = mongo_client["imoisture"]

db = SQLAlchemy()
app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///site.db"
db = SQLAlchemy(app)

app.config["SECRET_KEY"] = os.getenv("SQL_ACLCHEMY_KEY")

from core.models import User
from core.views import home

app.register_blueprint(home.home)
