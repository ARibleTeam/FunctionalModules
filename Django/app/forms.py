import os
from pathlib import Path
import shutil
import subprocess
import zipfile
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from app.models import FunctionalModule

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username']

class FunctionalModuleForm(forms.ModelForm):
    file = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': False}))
    
    class Meta:
        model = FunctionalModule
        fields = ['name', 'slug', 'type', 'description', 'groups', 'file', 'hello_message']
        widgets = {
            'groups': forms.CheckboxSelectMultiple,
        }
        labels = {
            'name': 'Название',
            'slug': 'Ссылка/Дирректория',
            'type': 'Тип модуля',
            'description': 'Описание',
            'groups': 'Группы',
            'hello_message': 'Приветсвенное сообщение',
        }
        help_texts = {
            'name': 'Введите название функционального модуля',
            'slug': 'Уникальный идентификатор для URL и название дирректории, где лежит проект (латинские буквы, цифры, дефисы и подчёркивания)',
            'type': 'Выберите тип модуля',
            'description': 'Краткое описание модуля',
            'groups': 'Группы, которые будут иметь доступ к модулю.\nAll - все имеют доступ.\nNone - никто не имеет доступ',
            'hello_message': 'Отправляется пользователю при открытии модуля',
        }


    def clean_groups(self):
        groups = self.cleaned_data.get('groups')

        # Преобразуем все объекты Group в строки, извлекая имя группы
        group_names = [group.name for group in groups]

        # Проверка, если список групп пустой
        if not group_names:
            raise ValidationError('Вы должны выбрать хотя бы одну группу.')

        # Проверка, если выбраны одновременно "All" и другие группы
        if 'All' in group_names and len(group_names) > 1:
            raise ValidationError('Если выбрана группа "All", нельзя выбирать другие группы.')

        # Проверка, если выбраны одновременно "None" и другие группы
        if 'None' in group_names and len(group_names) > 1:
            raise ValidationError('Если выбрана группа "None", нельзя выбирать другие группы.')

        # Если выбраны "All" или "None" по одному, разрешаем
        return groups  # Возвращаем исходные объекты Group

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            file_name, file_extension = os.path.splitext(file.name)
            if file_extension.lower() != '.zip':
                raise ValidationError("Пожалуйста, выберите файл с расширением .zip.")
            try:
                with zipfile.ZipFile(file, 'r') as zip_ref:
                    file_names = zip_ref.namelist()
                    if 'pyproject.toml' not in file_names:
                        raise ValidationError("Проект должен использовать пакетный менеджер UV")
                    
                    slug_path = Path(settings.MODULES_DIR) / self.cleaned_data['slug']
                    print(slug_path)
                    os.makedirs(slug_path, exist_ok=True)
                    zip_ref.extractall(slug_path)
                    
                    main_py_path = slug_path / 'main.py'
                    if not main_py_path.exists():
                        raise ValidationError(f"Файл main.py не найден в распакованном архиве {self.cleaned_data['slug']}.")
                    
                    self.cleaned_data['extracted_path'] = str(main_py_path)
            except zipfile.BadZipFile:
                raise ValidationError("Загруженный файл не является корректным ZIP-архивом.")
            
            return file
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if 'extracted_path' in self.cleaned_data:
            instance.path = self.cleaned_data['extracted_path']
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance