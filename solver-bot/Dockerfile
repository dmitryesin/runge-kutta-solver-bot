FROM python:3.13.3-slim

WORKDIR /solver-client

COPY solver-bot .
COPY .env .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "src/main/python/main.py"]