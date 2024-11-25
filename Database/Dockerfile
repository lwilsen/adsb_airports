FROM python:3.12-slim

RUN apt-get update && apt-get install -y sqlite3

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["sh","-c", "python3 /app/make_db.py && tail -f /dev/null"]
