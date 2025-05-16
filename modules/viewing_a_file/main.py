import sys
import os

sys.stdout.reconfigure(encoding='utf-8')  # Добавь эту строку в начало


print("Прикрепите файл", flush=True)
file_path = input()

# Проверяем, что файл существует и его расширение .txt
if not os.path.isfile(file_path):
    print("Ошибка: Указанный файл не существует.", flush=True)

if not file_path.lower().endswith('.txt'):
    print("Ошибка: Файл не является текстовым файлом (.txt).", flush=True)

# Открываем файл и считываем его содержимое
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        print(f"Результат: {content}", flush=True)  # Выводим содержимое файла
except Exception as e:
    print(f"Ошибка при чтении файла: {e}", flush=True)