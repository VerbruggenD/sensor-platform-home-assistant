# Use Python 3.9 as the base image
FROM python:3.9-slim

# Install supervisor
RUN apt-get update && \
    apt-get install -y supervisor && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory in the container
WORKDIR /app

# Copy application code and requirements to container
COPY requirements.txt .
COPY config_server.py .
COPY heartbeat_service.py .
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Install Python dependencies
RUN pip install paho-mqtt

# Create log directory for supervisor
RUN mkdir -p /var/log/supervisor

# Mount the config folder
VOLUME ["/app/config"]
VOLUME ["/app/log"]

# Expose MQTT port
EXPOSE 1883

# Run the supervisor when the container launches
CMD ["/usr/bin/supervisord"]
