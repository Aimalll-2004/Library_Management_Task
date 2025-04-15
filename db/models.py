from db.db_connection import db


customer_book = db.Table('customer_book',
    db.Column('customer_id', db.Integer, db.ForeignKey('Customers.id'), primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('Books.id'), primary_key=True),
    db.Column('date_borrowed', db.DateTime, nullable=False),
    db.Column('date_returned', db.DateTime, nullable=True)
)

class Author(db.Model):
  __tablename__ = "Authors"
  # Columns
  id = db.Column(db.Integer, primary_key=True)
  author_name = db.Column(db.String, nullable=False)


class Publisher(db.Model):
  __tablename__ = "Publishers"
  
  # Columns
  id = db.Column(db.Integer, primary_key=True)
  publisher_name = db.Column(db.String, nullable=False)


class Genre(db.Model):
  __tablename__ = "Genres"
  
  # Columns
  id = db.Column(db.Integer, primary_key=True)
  genre = db.Column(db.String, nullable=False)


class Book(db.Model):
  __tablename__ = "Books"
  
  # Columns
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String, nullable=False)
  author_id = db.Column(db.ForeignKey("Authors.id"), nullable=False)
  publisher_id = db.Column(db.ForeignKey("Publishers.id"), nullable=False)
  genre_id = db.Column(db.ForeignKey("Genres.id"), nullable=False)
  state = db.Column(db.Boolean, nullable=False)

  # Relationships
  author = db.relationship("Author", backref=db.backref("books", lazy="select")) 
  publisher = db.relationship("Publisher", backref=db.backref("books", lazy="select"))
  genre = db.relationship("Genre", backref=db.backref("books", lazy="select"))

  customers = db.relationship("Customer", secondary=customer_book, backref=db.backref("books", lazy="select"))

  def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author.author_name,
            'publisher': self.publisher.publisher_name,
            'genre': self.genre.genre,
            'state': self.state
        }


class Customer(db.Model):
  __tablename__ = "Customers"

  # Columns
  id = db.Column(db.Integer, primary_key=True)
  customer_name = db.Column(db.String, nullable=False)



