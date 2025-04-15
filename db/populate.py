from db.db_connection import db
from db.models import Author, Publisher, Genre, Book, Customer  

def populate_all():
    populate_authors()
    populate_genres()
    populate_publishers()
    populate_books()
    db.session.commit()


def populate_authors():
    author1 = Author(author_name="George Orwell")
    author2 = Author(author_name="Harper Lee")
    author3 = Author(author_name="Jane Austen")
    author4 = Author(author_name="Francesc Miralles and Hector Garcia")

    db.session.add_all([author1, author2, author3, author4])


def populate_genres():
    genre1 = Genre(genre="Fiction")
    genre2 = Genre(genre="Non-Fiction")
    genre3 = Genre(genre="Romance")
    genre4 = Genre(genre="Satire")
    genre5 = Genre(genre="Self Help")    


    db.session.add_all([genre1, genre2, genre3, genre4, genre5])


def populate_publishers():
    publisher1 = Publisher(publisher_name="Penguin Books")
    publisher2 = Publisher(publisher_name="J.B. Lippincott &amp; Co.")
    publisher3 = Publisher(publisher_name="T. Egerton")
    publisher4 = Publisher(publisher_name="Secker and Warburg")
    publisher5 = Publisher(publisher_name="Penguin Life")

    db.session.add_all([publisher1, publisher2, publisher3, publisher4, publisher5])


def populate_books():
    # Retrieve existing authors, publishers, and genres from the database by their integer IDs
    author1 = Author.query.get(1)  
    author2 = Author.query.get(2)  
    author3 = Author.query.get(3)  
    author4 = Author.query.get(4)  

    publisher1 = Publisher.query.get(1)  
    publisher2 = Publisher.query.get(2)  
    publisher3 = Publisher.query.get(3)  
    publisher4 = Publisher.query.get(4)  
    publisher5 = Publisher.query.get(5)  

    genre1 = Genre.query.get(1)  
    genre2 = Genre.query.get(2)  
    genre3 = Genre.query.get(3)  
    genre4 = Genre.query.get(4)  
    genre5 = Genre.query.get(5)  


    book1 = Book(
        title="1984", 
        author_id=author1.id,  
        publisher_id=publisher1.id,
        genre_id=genre1.id,
        state=True  
    )
    book2 = Book(
        title="To Kill a Mockingbird", 
        author_id=author2.id, 
        publisher_id=publisher2.id, 
        genre_id=genre1.id, 
        state=True
    )
    book3 = Book(
        title="Pride and Prejudice", 
        author_id=author3.id, 
        publisher_id=publisher3.id, 
        genre_id=genre3.id, 
        state=True
    )
    book4 = Book(
        title="Animal Farm", 
        author_id=author1.id, 
        publisher_id=publisher4.id, 
        genre_id=genre4.id, 
        state=True
    )
    book5 = Book(
        title="Ikigai", 
        author_id=author4.id, 
        publisher_id=publisher5.id, 
        genre_id=genre5.id, 
        state=True
    )

    # Add books to the session
    db.session.add_all([book1, book2, book3, book4, book5])

    
