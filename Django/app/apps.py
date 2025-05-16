from django.apps import AppConfig
from django.conf import settings
from pathlib import Path
import os
from django.db.utils import OperationalError, ProgrammingError

class appConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    verbose_name = 'Веб-приложение'
