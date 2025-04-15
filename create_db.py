from db.db_connection import db
from db.populate import populate_all
from app import app



def create_populate_db():
    with app.app_context():
        db.drop_all()
        # Create all tables
        db.create_all()
        populate_all()
        print("Database initialized and populated successfully!")

if __name__ == "__main__":
    create_populate_db()
