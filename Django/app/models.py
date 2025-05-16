# models.py
from pathlib import Path
import shutil
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User, Group

from main.settings import BASE_DIR

class FunctionalModule(models.Model):
    TYPES = [
        ('file2file', 'File to File'),
        ('file2text', 'File to Text'),
        ('text2text', 'Text to Text'),
        ('text2file', 'Text to File'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(max_length=250)
    slug = models.SlugField(unique=True)
    type = models.CharField(max_length=10, choices=TYPES)
    groups = models.ManyToManyField(Group, related_name='functional_modules')  # Изменена связь с ManyToManyField
    path = models.TextField(max_length=255, blank=True)
    hello_message = models.TextField(max_length=255)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        # Получаем путь к папке модуля
        module_path = Path(settings.MODULES_DIR) / self.slug
        # Удаляем папку с модулями, если она существует
        if module_path.exists() and module_path.is_dir():
            shutil.rmtree(module_path)  # Удаляем всю папку и её содержимое
        super().delete(*args, **kwargs)  # Вызываем стандартное удаление

    class Meta:
        verbose_name = 'функциональный модуль'
        verbose_name_plural = 'Функциональные модули'


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name


