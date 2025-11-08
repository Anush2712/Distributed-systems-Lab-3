FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Client.py directly (not from src folder)
COPY Client.py .

EXPOSE 8080

# Run Client.py
CMD ["python", "Client.py"]