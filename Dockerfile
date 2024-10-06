# Dockerfile
# 24.10.4

FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 8080
ENV PYTHONPATH /app/ajax
CMD [ "python3", "src/main.py" ]
