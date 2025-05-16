import uuid
from datetime import datetime  # ВАЖНО: используем datetime из datetime
import random
import sys
from PIL import Image, ImageDraw
import os


sys.stdout.reconfigure(encoding='utf-8')  # Добавь эту строку в начало

# Функция для рисования точек
def draw_random_dots(num_points, image_size=(100, 100)):
    # Создаем пустое изображение с белым фоном
    img = Image.new('RGB', image_size, color='white')
    draw = ImageDraw.Draw(img)

    # Рисуем случайные точки
    for _ in range(num_points):
        x = random.randint(0, image_size[0] - 1)
        y = random.randint(0, image_size[1] - 1)
        draw.point((x, y), fill='black')

    # Сохраняем изображение
    file_path = os.path.abspath(f"{uuid.uuid4()}_{datetime.now().strftime("%Y-%m-%d %H-%M-%S-%f")}.png")
    img.save(file_path)
    
    return file_path


print("Введите количество точек: ", flush=True)
num_points = input()

if not num_points.isdigit():
    print("Ошибка: ожидается число!")

else:
    # Рисуем точки и получаем путь к файлу
    file_path = draw_random_dots(int(num_points))

    # Выводим абсолютный путь к файлу
    print(f"Файл: {file_path}", flush=True)
