# main.py (FastAPI сервер)
from contextlib import suppress
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
from multiprocessing import cpu_count
import asyncio
import json
import shutil
from pathlib import Path
import psutil


PATH  = Path(__file__).resolve().parent.parent
MAX_CONCURRENT_PROCESSES = cpu_count() * 2  # CPU_COUNT * 2 — классическое правило "2 процесса на ядро".

app = FastAPI()
process_semaphore = asyncio.Semaphore(MAX_CONCURRENT_PROCESSES)  # Органичиваем количество подпроцессов.

@app.websocket("/ws/messages")
async def message_websocket(websocket: WebSocket):
    await websocket.accept()

    proc = None  # Для корректного завершения (проблема 5)

    try:
        await websocket.send_json({
            "status": "connected",
            "message": "WebSocket server is running on port 8001!"
        })

        # Получаем первое служебное сообщение
        init_data = await websocket.receive_json()
        app_slug = init_data.get("app_slug")

        async with process_semaphore:

            try:
                # Ожидаем запуск не более 3 минут
                async with asyncio.timeout(60*3):
                    proc = await run_script_instance(app_slug)   
                    print(f"[PID {proc.pid}] Процесс запущен!")
    
            except asyncio.TimeoutError:
                await websocket.send_json({"status": "error", "output": "Модуль запускается слишком долго!"})
                
                # Завершаем процесс и закрываем соединение
                if proc:
                    proc.terminate()
                    await proc.wait()
                await websocket.close()
                return  # Полный выход из функции
            
            while True:

                try:
                    # Ожидаем ответ модуля не более 60 секунд
                    async with asyncio.timeout(60):
                            output = await proc.stdout.readline()     
                except asyncio.TimeoutError:
                    await websocket.send_json({"status": "error", "output": "Модуль отвечает слишком долго!"})
                    
                    # Завершаем процесс и закрываем соединение
                    if proc:
                        proc.terminate()
                        await proc.wait()
                    await websocket.close()
                    return  # Полный выход из функции

                if not output:
                    break

                message = output.decode('utf-8', errors='replace').strip()
                is_error = any(keyword in message.lower() for keyword in ["error", "exception", "traceback"])
                
                if is_error:
                    await websocket.send_json({
                        "status": "error",
                        "output": "Критическая ошибка на стороне модуля!",
                    })

                        # Завершаем процесс и закрываем соединение
                    if proc:
                        proc.terminate()
                        await proc.wait()
                    await websocket.close()
                    return  # Полный выход из функции

                if "Введите" in message or "Прикрепите" in message:

                    await websocket.send_json({
                        "status": "received",
                        "output": message,
                    })

                    while True:
                        try:
                            # Ожидаем ввод не более 10 секунд
                            async with asyncio.timeout(10):
                                user_data = await websocket.receive_json()       
                        except asyncio.TimeoutError:
                            await websocket.send_json({"status": "error", "output": "Превышено время ожидания!"})
                            
                            # Завершаем процесс и закрываем соединение
                            if proc:
                                proc.terminate()
                                await proc.wait()
                            await websocket.close()
                            return  # Полный выход из функции

                        if isinstance(user_data, dict) and user_data.get("status") == "input":
                            user_input = user_data.get("value", "")

                            if "Прикрепите" in message:
                                user_input = Path(PATH) / "files" / str(user_input)

                            proc.stdin.write(f"{user_input}\n".encode())
                            await proc.stdin.drain()
                            break
                        else:
                            print(f"[ignored input]: {user_data}")
                            # Завершаем всё из-за некорректных данных
                            await websocket.send_json({
                                "status": "error",
                                "output": "Некорректный формат запроса"
                            })
                            if proc:
                                proc.terminate()
                                await proc.wait()
                            await websocket.close()
                            return  # Полный выход из обработчика

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
                    if not str(file_name).startswith(str(PATH / "modules")):
                        raise ValueError("Недопустимый путь к файлу.")
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
    finally:
        if proc:
            try:
                print(f"[PID {proc.pid}] Завершаем процесс (глубоко)...")
                kill_process_tree(proc.pid)
                await asyncio.sleep(0.5)  # Дать время на завершение
            except Exception as e:
                print(f"[PID {getattr(proc, 'pid', '?')}] Ошибка при завершении: {e}")
        with suppress(Exception):
            await websocket.close()




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


def kill_process_tree(pid):
    try:
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        parent.kill()
    except Exception as e:
        print(f"[PID {pid}] Возможно, процесс уже был убит: {e}")


if __name__ == "__main__":
    app.run()