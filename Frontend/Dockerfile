FROM python:3.12-slim 

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8001

CMD ["streamlit", "run", "adsb_front.py", "--server.port", "8001", "--server.address", "0.0.0.0"]
