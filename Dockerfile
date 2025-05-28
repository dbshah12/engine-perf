# Use secure Python base
FROM python:3.10-slim-bookworm

# Install telegraf
RUN apt-get update && \
    apt-get install -y wget gnupg2 curl && \
    wget -qO- https://repos.influxdata.com/influxdata-archive.key | gpg --dearmor > /etc/apt/trusted.gpg.d/influxdata-archive.gpg && \
    echo "deb https://repos.influxdata.com/debian stable main" > /etc/apt/sources.list.d/influxdata.list && \
    apt-get update && \
    apt-get install -y telegraf && \
    apt-get clean

# Set workdir and install Python deps
WORKDIR /app
COPY ./scripts/engine_performance/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy full app
COPY . .
