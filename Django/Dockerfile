FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=main.settings

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ⛳️ Сначала копируем проект
COPY . .

# 🧹 Собираем статику
RUN python manage.py collectstatic --noinput

# 🔁 Монтируем тома (на этапе контейнера)
VOLUME /app/modules /app/files

# 🚀 Запуск через gunicorn
CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
