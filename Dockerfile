FROM python:3.12.3

# Set WORKDIR
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Start gunicorn server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stock_insight.wsgi:application", "--workers", "3", "--timeout", "120"]