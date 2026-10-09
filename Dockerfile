FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 MEDIA_ROOT=/data/photos
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput && useradd -u 10001 app && mkdir -p /data/photos && chown -R app:app /data
ENV ENVIRONMENT=production
USER app
EXPOSE 8000
CMD ["sh","scripts/start.sh"]
