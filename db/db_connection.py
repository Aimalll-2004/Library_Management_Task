from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()


db = SQLAlchemy()

def init_db(app):
  app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URI")  
  db.init_app(app)
