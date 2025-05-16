from pathlib import Path
import shutil
import subprocess

from django.http import FileResponse, Http404, JsonResponse
from app.models import FunctionalModule
from main.settings import BASE_DIR


class Service:
    @staticmethod
    def get_available_apps(request):
        AVAILABLE_APPS = Service.get_available_apps_from_db()
        
        if request.user.is_authenticated:
            user_groups = set(request.user.groups.values_list('name', flat=True))  # Список групп пользователя

            available_apps = []
            for app in AVAILABLE_APPS:
                # Получаем группы для приложения (если они есть)
                app_groups = set(app['group'].split('; '))  # Преобразуем строку групп в множество

                # Проверяем, если приложение связано с группой 'All', то доступно всем
                if 'All' in app_groups or app_groups.intersection(user_groups):
                    available_apps.append(app)

            return available_apps
        else:
            # Для неавторизованных пользователей доступны только приложения с группой 'All'
            return [app for app in AVAILABLE_APPS if 'All' in app['group'].split('; ')]
    
    @staticmethod
    # Функция для получения всех функциональных модулей из базы данных в том же формате, как в AVAILABLE_APPS
    def get_available_apps_from_db():
        modules = FunctionalModule.objects.all()
        formatted_modules = [
            {
                "name": module.name,
                'description': module.description,
                "slug": module.slug,
                "type": module.type,
                "group": "; ".join(group.name for group in module.groups.all()),  # Собираем все группы через точку с запятой
                "hello_message": Path(module.hello_message),
            }
            for module in modules
        ]
        return formatted_modules


    @staticmethod
    def get_app_name(slug):
        # Получаем все данные из базы в нужном формате
        AVAILABLE_APPS = Service.get_available_apps_from_db()

        # Ищем приложение по slug в AVAILABLE_APPS
        app = next((app for app in AVAILABLE_APPS if app['slug'] == slug), None)
        
        # Если приложение найдено, возвращаем его имя, иначе возвращаем None
        if app:
            return app['name']
        else:
            return None
