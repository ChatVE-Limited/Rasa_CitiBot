FROM rasa/rasa:3.6.21

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

RUN if [ ! -f "/app/models/model.tar.gz" ]; then echo "No trained model found!"; exit 1; fi

CMD ["rasa", "run", "--endpoints", "endpoints.production.yml", "--enable-api", "--cors", "*", "--debug", "--port", "5005"]
