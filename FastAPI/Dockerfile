FROM python:3.9-slim

# Установка системных зависимостей для OpenCV и других библиотек
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

VOLUME /app/modules /app/files

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
