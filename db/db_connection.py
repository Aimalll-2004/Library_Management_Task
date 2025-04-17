from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()


db = SQLAlchemy()

def init_db(app):
  app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://admin:mysecretpassword@localhost:5432/pg-container"
  db.init_app(app)
