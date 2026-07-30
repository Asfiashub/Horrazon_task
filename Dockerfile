FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple -r requirements.txt

COPY app/ ./app/
COPY data/ ./data/

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "-m", "app.main"]