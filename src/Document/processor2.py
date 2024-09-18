import json
import logging
import os
import re
from datetime import datetime

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

import pika
import psycopg2
import PyPDF2
from sentence_transformers import SentenceTransformer
import time

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
model = SentenceTransformer('all-MiniLM-L6-v2')

# Set up logging
logging.basicConfig(filename='document_processor.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def process_pdf(pdf_path, min_length=5):
    results = []

    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        # Initialize variables to store sentence groups
        sentence_buffer = []
        page_buffer = []
        
        # Iterate through all pages
        for page_num, page in enumerate(reader.pages):
            # Extract text from the page
            text = page.extract_text()
            if text:
                # Sanitize and split the text
                sanitized_text = sanitize_text(text)
                sentences = split_by_stop_marks(sanitized_text)
                
                # Add sentences and page numbers to buffers
                for sentence in sentences:
                    # Skip empty sentences and those shorter than min_length
                    if sentence.strip() and len(sentence.strip()) >= min_length:
                        sentence_buffer.append(sentence)
                        page_buffer.append(page_num + 1)
                        
                        # Check if we have a complete group of 5 sentences
                        if len(sentence_buffer) == 5:
                            results.append({
                                'page': page_buffer[0],  # Page of the first sentence in the group
                                'group': sentence_buffer
                            })
                            # Reset buffers
                            sentence_buffer = []
                            page_buffer = []

        # Handle any remaining sentences that didn't form a full group
        if sentence_buffer:
            results.append({
                'page': page_buffer[0],  # Page of the first sentence in the remaining group
                'group': sentence_buffer
            })

    return results

def split_by_stop_marks(text):
    # Regular expression to split by period (.), question mark (?), and exclamation mark (!)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return sentences

def sanitize_text(text):
    # Remove all line breaks (both \n and \r)
    sanitized_text = text.replace('\n', ' ').replace('\r', ' ')
    # Remove multiple spaces and trim leading/trailing spaces
    sanitized_text = re.sub(r'\s+', ' ', sanitized_text).strip()
    return sanitized_text

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
                        page = paragraph['page']
                        para =" ".join(paragraph['group']);
                        processed_chunk = preprocess_text(" ".join(paragraph['group']))

                        logging.info(f"page {page} processed_chunk {processed_chunk}.")

                        # Skip empty processed_chunk
                        if not processed_chunk:
                            logging.info(f"Skipping empty processed_chunk for paragraph {idx}")
                            continue

                        embedding = model.encode(processed_chunk)
                        cur.execute("""
                            INSERT INTO public."DocumentSegments" ("DocumentId", "TextContent", "Embedding", "UploadedDate","PageId")
                            VALUES (%s, %s, %s, %s,%s)
                        """, (document_id, para, (embedding.tolist(),), datetime.utcnow().isoformat(),page))
                
                        # Commit once after all inserts
                        conn.commit()
                    except Exception as e:
                        logging.error(f"An error occurred: {e}")
        logging.info(f"Stored {len(paragraphs)} paragraphs for document_id {document_id} in the database.")

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        # Handle exceptions or rollback if necessary

# Define a callback function to handle messages
def callback(ch, method, properties, body):
    # Decode the body to a JSON object
    data = json.loads(body)
    
    # Extract the necessary information from the message body
    file_path = data["FilePath"]
    file_name = data["FileName"]
    file_id = data["Id"]
    
    logging.info(f"Processing file: {file_name}")

    sentence_groups = process_pdf(file_path)

    store_in_database(sentence_groups, file_id)

# Fetch RabbitMQ connection parameters from environment variables
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))

connection_params = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)

queue_name = 'documentQueue'
retry_delay_seconds = 60  # 1 minutes (60 seconds)

def connect_to_rabbitmq():
    while True:
        try:
            # Try to create a connection to RabbitMQ
            logging.info(f'Trying to connect to RabbitMQ at {rabbitmq_host}:{rabbitmq_port}')
            connection = pika.BlockingConnection(connection_params)
            channel = connection.channel()
            
            # Declare a queue (create it if it does not exist)
            logging.info(f'Connected. Declaring queue {queue_name}')
            channel.queue_declare(queue=queue_name, durable=True)
            
            # Set up the consumer
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True, consumer_tag='document_processor')
            
            logging.info('Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            logging.error(f'Connection to RabbitMQ failed: {e}. Retrying in {retry_delay_seconds // 60} minutes...')
            time.sleep(retry_delay_seconds)

connect_to_rabbitmq()
