FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

COPY . .

CMD ["sh", "-c", "flask db upgrade && gunicorn -b 0.0.0.0:5000 yacut:app"]
