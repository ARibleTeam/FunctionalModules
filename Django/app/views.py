import json
import os
from pathlib import Path
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import FileResponse, Http404, JsonResponse
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from app.forms import RegisterForm
from app.servise import Service
from main.settings import BASE_DIR, FILES_DIR
from django.contrib.auth.models import Group


# Функция для получения всех функциональных модулей из базы данных в том же формате, как в AVAILABLE_APPS

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()  # Получаем пользователя из формы
            login(request, user)  # Авторизуем пользователя
            return redirect('/')  # Перенаправляем на главную страницу (замените 'home' на ваш маршрут)
        else:
            messages.error(request, "Неправильный логин или пароль.")  
    else:
        form = AuthenticationForm()

    return render(request, 'registration/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            default_group, created = Group.objects.get_or_create(name='Default')
            user.groups.add(default_group)
            
            # Вход пользователя после регистрации
            login(request, user)

            # Перенаправление на страницу входа (или на любую нужную страницу)
            return redirect('/')
    else:
        form = RegisterForm()
    
    return render(request, 'registration/register.html', {'form': form})

def index(request):
    apps = Service.get_available_apps(request)
    return render(request, 'start-menu.html', {'apps': apps})

def chat_view(request, app_slug):
    apps = Service.get_available_apps(request)
    app = next((app for app in apps if app["slug"] == app_slug), None)

    if not app:
        return JsonResponse({'error': 'Приложение не найдено'}, status=404)

    return render(request, 'chat-menu.html', {'apps': apps, 'active_app': app})

# по запрошенному названию файла выгружает файл donwloads/file_name.png
def download_file_view(request, file_name):
    file_path = FILES_DIR / file_name

    if not file_path.exists():
        return FileResponse(open(BASE_DIR / 'app' / 'static' / 'img' / 'not-found.png', 'rb'), as_attachment=True, filename="Упс.png")

    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
    
    def cleanup_file():
        try:
            file_path.unlink()
        except Exception as e:
            print(f"Ошибка удаления файла: {e}")

    # Удаляем файл после завершения ответа
    # response.close = lambda: (super(type(response), response).close(), cleanup_file())

    return response

# Сохраняет файл на сервере, возвращает его  название на сервере. (для отображения на фронте)
def file_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage(location=os.path.join(FILES_DIR))  # Путь для сохранения файла
        filename = fs.save(uploaded_file.name.replace(' ', ''), uploaded_file)  # Сохраняем файл

        #app_name = request.POST.get('app_name')

        #app = next((app for app in AVAILABLE_APPS if app["name"] == app_name), None)

        #result = Service.run_script(app["path"], Path(BASE_DIR) / "media" / "uploads" / filename)

        # Удаляем
        #Path(Path(BASE_DIR) / "media" / "uploads" / filename).unlink()

        #if (result.lower()).count("ошибка") > 0:
            #return JsonResponse({'success': True, 'response': result}) 
        #elif(app["type"] != "file2file"):
            #return JsonResponse({'success': True, 'response': result})
        
        #path = Service.copy_and_remove_file(result)
        
        return JsonResponse({'success': True, 'response': filename})