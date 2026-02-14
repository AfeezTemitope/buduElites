FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for mysqlclient and psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files for Django admin
RUN python manage.py collectstatic --noinput 2>/dev/null || true

EXPOSE ${PORT:-8000}

CMD gunicorn befa.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
