# main.py (FastAPI сервер)
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import asyncio
import json
import shutil
from pathlib import Path

PATH  = Path(__file__).resolve().parent.parent

app = FastAPI()

def copy_and_remove_file(file_path):

    file_path = file_path.replace("\n", "").replace("\r", "")

    # Путь к новой директории
    new_dir = Path(PATH) / "files"

    # Создаем новую директорию, если она не существует
    new_dir.mkdir(parents=True, exist_ok=True)

    # Получаем имя файла из пути
    file_name = Path(file_path).name

    # Путь к новому файлу
    new_file_path = new_dir / file_name


    # Копируем файл в новую директорию
    shutil.copy(file_path, new_file_path)

    # Удаляем оригинальный файл
    Path(file_path).unlink()

    return str(file_name)  # Возвращаем название файла


@app.websocket("/ws/messages")
async def message_websocket(websocket: WebSocket):
    await websocket.accept()

    async def run_script_instance(app_slug):
        script_path = PATH / "modules" / app_slug
        print(f"Запускаю скрипт из {script_path}")
        proc = await asyncio.create_subprocess_exec(
            'uv', 'run', 'main.py',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=str(script_path)
        )
        return proc

    try:
        await websocket.send_json({
            "status": "connected",
            "message": "WebSocket server is running on port 8001!"
        })

        # Получаем первое служебное сообщение
        init_data = await websocket.receive_json()
        app_slug = init_data.get("app_slug")

        while True:
            proc = await run_script_instance(app_slug)

            while True:
                output = await proc.stdout.readline()
                if not output:
                    break

                message = output.decode('utf-8', errors='replace').strip()
                is_error = any(keyword in message.lower() for keyword in ["error", "exception", "traceback"])
                
                if is_error:
                    await websocket.send_json({
                        "status": "error",
                        "output": "Критическая ошибка на стороне модуля!",
                    })

                    await websocket.close()
                    return

                if "Введите" in message or "Прикрепите" in message:

                    await websocket.send_json({
                        "status": "received",
                        "output": message,
                    })

                    # Ждём специальный ввод с ключом 'status': 'input'
                    while True:
                        user_data = await websocket.receive_json()
                        if isinstance(user_data, dict) and user_data.get("status") == "input":
                            user_input = user_data.get("value", "")

                            if "Прикрепите" in message:
                                user_input = Path(PATH) / "files" / str(user_input)

                            proc.stdin.write(f"{user_input}\n".encode())
                            await proc.stdin.drain()
                            break
                        else:
                            print(f"[ignored input]: {user_data}")
                elif "Результат" in message or "Ошибка" in message:
                    await websocket.send_json({
                        "status": "received",
                        "output": message,
                    })
                    await proc.wait()
                    break  # перезапуск
                elif "Файл" in message:
                    file_name = message.replace('Файл: ', '')
                    file_name = file_name.replace('Файл:', '')
                    
                    new_file_name = copy_and_remove_file(file_name)

                    await websocket.send_json({
                        "status": "file",
                        "file_name": new_file_name,
                    })

    except WebSocketDisconnect:
        print("Клиент отключился")
    except Exception as e:
        await websocket.send_json({
            "status": "error",
            "output": "Критическая ошибка на стороне модуля!",
        })
        print(f"Что-то странное", e)



if __name__ == "__main__":
    app.run()