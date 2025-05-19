from ultralytics import YOLO
import sys
import os
import logging

sys.stdout.reconfigure(encoding='utf-8')  # Добавь эту строку в начало
logging.disable(logging.CRITICAL)  # Отключаем логи

# Загрузка модели
model = YOLO("yolov5n.pt")

print("Прикрепите и отправьте изображение для работы", flush=True)
# Получаем путь к файлу
file_path = input()

# Проверяем, что файл существует и его расширение .txt
if not os.path.isfile(file_path):
    print("Ошибка: Указанный файл не существует.", flush=True)

# Детекция объектов
results = model(file_path, verbose=False)

# Сохранение и получение полного пути
for result in results:
    relative_path = result.save()  # Относительный путь (например: 'runs/detect/predict/bus.jpg')
    absolute_path = os.path.abspath(relative_path)  # Преобразуем в абсолютный
    print(f"Файл: {absolute_path}", flush=True)
