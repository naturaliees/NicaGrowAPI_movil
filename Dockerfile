FROM python:3.12-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 APP_ENV=production PORT=8000
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates libltdl7 libkrb5-3 libgssapi-krb5-2 libstdc++6 unixodbc \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.lock.txt requirements.azure.txt ./
RUN python -m pip install --no-cache-dir -r requirements.azure.txt
COPY api ./api
COPY config ./config
COPY manage.py gunicorn.conf.py startup.sh ./
RUN useradd --uid 10001 --create-home appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["sh", "startup.sh"]
