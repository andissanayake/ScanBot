import pika
import os

# Fetch RabbitMQ connection parameters from environment variables
rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))

connection_params = pika.ConnectionParameters(host=rabbitmq_host, port=rabbitmq_port)

# Create a connection to RabbitMQ
connection = pika.BlockingConnection(connection_params)
channel = connection.channel()

# Declare a queue (create it if it does not exist)
queue_name = 'documentQueue'
print(rabbitmq_host,rabbitmq_port,queue_name)
channel.queue_declare(queue=queue_name, durable=True)

# Define a callback function to handle messages
def callback(ch, method, properties, body):
    print(f"Received {body}")

# Set up the consumer
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True,consumer_tag='document_processor')

print('Waiting for messages. To exit press CTRL+C')
channel.start_consuming()

