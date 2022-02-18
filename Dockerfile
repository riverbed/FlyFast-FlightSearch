FROM python:3.7-slim-buster
RUN apt update
WORKDIR /app
COPY . .

RUN apt-get update && apt-get install build-essential -y

RUN pip install -r requirements.txt

EXPOSE 8080
ENV PYTHONPATH /app/ajax
CMD [ "python3", "flightsearch.py" ]
