FROM python:3.8

WORKDIR /app

COPY src/ .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 0 main:app
