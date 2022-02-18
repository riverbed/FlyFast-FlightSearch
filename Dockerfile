FROM python:3.7-slim-buster
RUN apt update
WORKDIR /app

RUN apt-get update && apt-get install build-essential -y


RUN python3 -m pip install tornado==5.1.1
RUN python3 -m pip install requests py_zipkin
RUN pip install opentelemetry-exporter-otlp
COPY . .
EXPOSE 8080
ENV PYTHONPATH /app/ajax
CMD [ "python3", "flightsearch.py" ]
