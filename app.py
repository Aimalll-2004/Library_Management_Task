from flask import Flask, render_template, jsonify, request
import configparser
import requests
import logging
from flask_cors import CORS
from sqlalchemy import select
from db.db_connection import init_db, db
from db.models import Author, Publisher, Genre, Book, Customer, customer_book


app = Flask(__name__, static_url_path='/static', static_folder='static')

init_db(app)

CORS(app)

# Configure logging to DEBUG level for detailed logs
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO to DEBUG
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Load the configuration from the config.ini file
config = configparser.ConfigParser()
config.read('config.ini')

# Get the API key and URL from the configuration
try:
    GEMINI_API_KEY = config.get('API', 'GEMINI_API_KEY')
    GEMINI_API_URL = config.get('API', 'GEMINI_API_URL')
    logging.info("Gemini API configuration loaded successfully.")
except Exception as e:
    logging.error("Error reading config.ini: %s", e)
    GEMINI_API_KEY = None
    GEMINI_API_URL = None

# Route to serve the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route to serve viewer.html
@app.route('/viewer.html')
def viewer():
    return render_template('viewer.html')

@app.route("/api/display_books", methods=["GET"])
def get_all_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])

@app.route("/api/display_entity", methods=["POST"])
def get_entity():
    entity_data = request.json
    entity_id = entity_data.get("id")
    entity_type = entity_data.get("entity")

    if entity_type == "Author":
        author = Author.query.get(entity_id)
        author_name = author.author_name if author else "Author not found"
        return jsonify({"Author": author_name})

    elif entity_type == "Publisher":
        publisher = Publisher.query.get(entity_id)
        publisher_name = publisher.publisher_name if publisher else "Publisher not found"
        return jsonify({"Publisher":publisher_name})

    elif entity_type == "Genre":
        genre = Genre.query.get(entity_id)
        genre_name = genre.genre if genre else "Genre not found"
        return jsonify({"Genre": genre_name})
    
    elif entity_type == "Book":
        book = Book.query.get(entity_id)
        return jsonify({"Title":book.title,
                        "Author":book.author.author_name,
                        "Publisher":book.publisher.publisher_name,
                        "Genre":book.genre.genre,
                        "State":book.state})
    
    else:
        return jsonify({"error": "Invalid entity type"}), 400

@app.route('/api/borrow_book', methods=['POST'])
def borrow_book():
    book_id = request.json.get("bookId")
    book = Book.query.get(book_id)
    borrower_name = request.json.get("borrowerName")
    borrow_date = request.json.get("borrowDate")

    customer = Customer.query.filter_by(customer_name=borrower_name).first()
    if not customer:
        customer = Customer(customer_name=borrower_name)
        db.session.add(customer)
        db.session.commit()

    insert_stmt = customer_book.insert().values(
        customer_id=customer.id,
        book_id=book_id,
        date_borrowed=borrow_date
    )
    db.session.execute(insert_stmt)

    book.state = False
    db.session.commit()

    return jsonify({"message": f"Book ID {book_id} borrowed by {borrower_name} on {borrow_date}."})


@app.route('/api/return_book', methods=['POST'])
def return_book():
    book_id = request.json.get("bookId")
    return_date = request.json.get("returnDate")

    book = Book.query.get(book_id)

    result = db.session.execute(
        select(customer_book.c.customer_id).where(customer_book.c.book_id == book_id)
    ).first()
    if result is None:
        return jsonify({"error": f"No customer found borrowing book ID {book_id}."}), 404

    customer_id = result[0]
    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found."}), 404
    customer_name = customer.customer_name
    
    assoc_remove_stmt = customer_book.delete().where(customer_book.c.book_id == book_id)
    db.session.execute(assoc_remove_stmt)

    remaining_books = db.session.execute(
        select(customer_book.c.book_id).where(customer_book.c.customer_id == customer_id)
    ).fetchall()

    if not remaining_books:
        db.session.delete(customer)

    book.state = True
    db.session.commit()

    return jsonify({"message": f"Book ID {book_id} returned by {customer_name} on {return_date}."})


@app.route('/api/clear_borrowing_data', methods=['POST'])
def clear_borrrowing_data():
    db.session.execute(customer_book.delete())
    db.session.query(Customer).delete()
    db.session.commit()
    return jsonify({"message": "All borrowing data has been cleared."})


# API route to fetch description from Gemini API
@app.route('/api/description', methods=['GET'])
def get_description():
    entity_name = request.args.get('name')
    logging.debug(f"Received request for entity name: {entity_name}")  # Changed to DEBUG

    if not entity_name:
        logging.warning("Missing entity name in request.")
        return jsonify({'error': 'Missing entity name'}), 400

    if not GEMINI_API_URL or not GEMINI_API_KEY:
        logging.error("Gemini API configuration missing.")
        return jsonify({'error': 'Server configuration error'}), 500

    # Prepare the JSON payload with explicit instructions
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Provide a detailed description of '{entity_name}'"
                            "If it is a book include information about the setting, characters, themes, key concepts, and its influence. "
                            "Do not include any concluding remarks or questions."
                            "Do not mention any Note at the end about not including concluding remarks or questions."
                        )
                    }
                ]
            }
        ]
    }

    # Construct the API URL with the API key as a query parameter
    api_url_with_key = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"

    headers = {
        "Content-Type": "application/json"
    }

    # Log the API URL and payload for debugging
    logging.debug(f"API URL: {api_url_with_key}")
    logging.debug(f"Payload: {payload}")

    try:
        # Make the POST request to the Gemini API
        response = requests.post(
            api_url_with_key,  # Include the API key in the URL
            headers=headers,
            json=payload,
            timeout=10  # seconds
        )
        logging.debug(f"Gemini API response status: {response.status_code}")  # Changed to DEBUG

        if response.status_code != 200:
            logging.error(f"Failed to fetch description from Gemini API. Status code: {response.status_code}")
            logging.error(f"Response content: {response.text}")
            return jsonify({
                'error': 'Failed to fetch description from Gemini API',
                'status_code': response.status_code,
                'response': response.text
            }), 500

        response_data = response.json()
        # Extract the description from the response
        description = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No description available.')
        logging.debug(f"Fetched description: {description}")  # Changed to DEBUG

        return jsonify({'description': description})

    except requests.exceptions.RequestException as e:
        logging.error(f"Exception during Gemini API request: {e}")
        return jsonify({'error': 'Failed to connect to Gemini API', 'message': str(e)}), 500
    except ValueError as e:
        logging.error(f"JSON decoding failed: {e}")
        return jsonify({'error': 'Invalid JSON response from Gemini API', 'message': str(e)}), 500
    except Exception as e:
        logging.exception(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
