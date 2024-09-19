# Use the official PostgreSQL image as the base image
FROM postgres:latest

# Install dependencies and pgvector
RUN apt-get update && \
    apt-get install -y postgresql-server-dev-16 build-essential git && \
    git clone --branch v0.5.0 https://github.com/pgvector/pgvector.git /pgvector && \
    cd /pgvector && \
    make && \
    make install && \
    rm -rf /pgvector && \
    apt-get remove --purge -y postgresql-server-dev-16 build-essential git && \
    apt-get autoremove -y && \
    apt-get clean

# Copy the custom entrypoint script
COPY docker-entrypoint-initdb.d /docker-entrypoint-initdb.d

# Ensure scripts in docker-entrypoint-initdb.d are executable
RUN chmod a+r /docker-entrypoint-initdb.d/*.sql
