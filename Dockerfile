FROM python:3.8

WORKDIR /app

RUN mkdir /data

COPY src/ .
COPY requirements.txt .

RUN apt-get update && apt-get install texlive -y
RUN pip install -r requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 4 --timeout 0 main:app
