import os
import time
from pathlib import Path
from datetime import datetime, timedelta


PATH  = Path(__file__).resolve().parent.parent

FILES_DIR = Path(PATH) / "files"
CLEAN_INTERVAL = 30  # минут

def clean_old_files():
    now = datetime.now()
    for file in Path(FILES_DIR).glob("*"):
        if file.is_file():
            file_time = datetime.fromtimestamp(file.stat().st_mtime)
            if (now - file_time) > timedelta(minutes=CLEAN_INTERVAL):
                file.unlink()
                print(f"Deleted {file.name}")

if __name__ == "__main__":
    print("Сервис по очистке запущен!")
    while True:
        clean_old_files()
        time.sleep(60 * CLEAN_INTERVAL)  # Проверка каждые 30 минут