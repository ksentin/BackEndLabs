FROM python:3.11-slim-bullseye

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install -r requirements.txt

COPY . /app

ENV FLASK_APP=myapp

CMD flask run --host=0.0.0.0 -p 5004