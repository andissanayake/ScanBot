import pika
import os
import json
import PyPDF2
import psycopg2
from datetime import datetime
import logging
from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
model = SentenceTransformer('all-MiniLM-L6-v2')

# Set up logging
logging.basicConfig(filename='document_processor.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Fetch RabbitMQ connection parameters from environment variables
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))

connection_params = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)

# Create a connection to RabbitMQ
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

# Declare a queue (create it if it does not exist)
queue_name = 'documentQueue'
logging.info(f'Connecting to RabbitMQ at {rabbitmq_host}:{rabbitmq_port} with queue {queue_name}')
channel.queue_declare(queue=queue_name, durable=True)

# Define a callback function to handle messages
def callback(ch, method, properties, body):
    # Decode the body to a JSON object
    data = json.loads(body)
    
    # Extract the necessary information from the message body
    file_path = data["FilePath"]
    file_name = data["FileName"]
    file_id = data["Id"]
    
    logging.info(f"Processing file: {file_name}")

    # Extract text in chunks from the PDF file
    text = extract_text_in_chunks(file_path, chunk_size=100)

    sentences = nltk.sent_tokenize(text)
    store_in_database(sentences, file_id)

def extract_text_in_chunks(pdf_path, chunk_size=100):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        
        for start_page in range(0, num_pages, chunk_size):
            end_page = min(start_page + chunk_size, num_pages)
            for page_num in range(start_page, end_page):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
    return text

def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Lowercase all tokens
    tokens = [word.lower() for word in tokens]
    
    # Remove punctuation
    tokens = [word for word in tokens if word.isalnum()]
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(word) for word in tokens]

    return ' '.join(tokens)

def store_in_database(paragraphs, document_id):
    try:
        # Connect to your PostgreSQL database
        with psycopg2.connect(
            dbname="UnifiedAppDb",
            user="postgres",
            password="YourStrong!Passw0rd",
            host="postgres",
            port="5432"
        ) as conn:
            with conn.cursor() as cur:
                for idx, paragraph in enumerate(paragraphs, start=1):
                    try:
                        processed_chunk = preprocess_text(paragraph)
                        # Skip empty processed_chunk
                        if not processed_chunk:
                            logging.info(f"Skipping empty processed_chunk for paragraph {idx}")
                            continue

                        embedding = model.encode(processed_chunk)
                        cur.execute("""
                            INSERT INTO public."DocumentSegments" ("DocumentId", "TextContent", "Embedding", "UploadedDate")
                            VALUES (%s, %s, %s, %s)
                        """, (document_id, paragraph, (embedding.tolist(),), datetime.utcnow().isoformat()))
                
                        # Commit once after all inserts
                        conn.commit()
                    except Exception as e:
                        logging.error(f"An error occurred: {e}")
        logging.info(f"Stored {len(paragraphs)} paragraphs for document_id {document_id} in the database.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        # Handle exceptions or rollback if necessary

# Set up the consumer
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True, consumer_tag='document_processor')

logging.info('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()
