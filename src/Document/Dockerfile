# Use a base image with Python 3.11
FROM python:3.11-slim

# Set environment variables to ensure that Python buffers stdout and stderr
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Download NLTK data
RUN python -m nltk.downloader all
#RUN python -m nltk.downloader punkt stopwords wordnet

# Define the command to run the application
CMD ["python", "processor2.py"]
