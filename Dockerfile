FROM rasa/rasa:3.6.21

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3.10-venv \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN test -f "/app/models/20250318-113652-tranquil-backpack.tar.gz" || (echo "No trained model found! Exiting..." && exit 1)

# Start Rasa server with appropriate configurations
CMD ["rasa", "run", "--endpoints", "endpoints.production.yml", "--enable-api", "--cors", "*", "--debug", "--port", "5005"]
