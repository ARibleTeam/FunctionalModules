import os
from pathlib import Path
import subprocess
import zipfile
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib import messages
from app.forms import FunctionalModuleForm
from app.models import FunctionalModule


class UserInline(admin.TabularInline):
    model = Group.user_set.through
    extra = 1  # Количество пустых полей для добавления новых пользователей

class GroupInline(admin.TabularInline):
    model = FunctionalModule.groups.through  # Связь многие ко многим через промежуточную модель
    extra = 1  # Количество пустых полей для добавления новых групп

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Переопределяем фильтрацию для поля 'functionalmodule'
        # Это нужно для того, чтобы исключить связанные с группами "None" и "All"
        formset.form.base_fields['functionalmodule'].queryset = FunctionalModule.objects.exclude(groups__name__in=['None', 'All']).distinct()

        return formset
    
# Теперь создаем админку с использованием кастомной формы
class CustomGroupAdmin(admin.ModelAdmin):
    inlines = [UserInline, GroupInline]
    fieldsets = [
        (None, {'fields': ('name',)}),
    ]


    def get_queryset(self, request):
        # Получаем стандартный queryset
        queryset = super().get_queryset(request)
        
        # Фильтруем группы 'None' и 'All', чтобы они не отображались в админке
        return queryset.exclude(name__in=['None', 'All'])

    def get_inlines(self, request, obj=None):
        # Получаем изначальный список inlines
        inlines = super().get_inlines(request, obj)
        
        # Если группа 'None' или 'All', убираем возможность редактировать пользователей
        if obj and obj.name in ['None', 'All']:
            inlines = [inline for inline in inlines if inline != UserInline]
        
        return inlines

    def get_fieldsets(self, request, obj=None):
        # Получаем стандартные fieldsets
        fieldsets = super().get_fieldsets(request, obj)
        
        # Если редактируем группу 'None', 'All' или 'Default', делаем поле 'name' только для чтения
        if obj and obj.name in ['None', 'All', 'Default']:  # Для редактируемых групп
            fieldsets[0][1]['fields'] = ['name']
            self.readonly_fields = ['name']
        else:
            # Для новых групп или других групп, поле 'name' редактируемое
            self.readonly_fields = []

        return fieldsets

    def save_model(self, request, obj, form, change):
        # Сохраняем объект
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление для группы 'Default'
        if obj and obj.name == 'Default':
            return False
        return super().has_delete_permission(request, obj)

class CustomUserAdmin(admin.ModelAdmin):
    # Поля, которые будут отображаться в форме редактирования
    fieldsets = [
        (None, {'fields': ['username']}),  # Поле для пароля
        ('Permissions', {'fields': ['groups']}),  # Поля для групп и прав
    ]
    
    list_display = ('username', 'is_superuser')
    search_fields = ('username',)
    filter_horizontal = ('groups',)  # Горизонтальный выбор для групп пользователей

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Проверяем, что поле это для groups
        if db_field.name == 'groups':
            # Получаем все группы, кроме тех, которые называются 'None' или 'All'
            kwargs['queryset'] = Group.objects.exclude(name__in=['None', 'All'])
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class FunctionalModuleAdmin(admin.ModelAdmin):
    form = FunctionalModuleForm  # Указываем форму для админки
    list_display = (
        'get_name', 
        'get_slug', 
        'get_type', 
        'get_description', 
        'groups_display', 
        'get_hello_message'
    )
    search_fields = ('name',)
    actions = None
    
    def save_model(self, request, obj, form, change):
        obj.save()

        # Методы для отображения полей с русскими названиями
    def get_name(self, obj):
        return obj.name
    get_name.short_description = 'Название'

    def get_slug(self, obj):
        return obj.slug
    get_slug.short_description = 'Ссылка/Дирректория'

    def get_type(self, obj):
        return obj.type
    get_type.short_description = 'Тип'

    def get_description(self, obj):
        return obj.description
    get_description.short_description = 'Описание'

    def get_hello_message(self, obj):
        return obj.hello_message
    get_hello_message.short_description = 'Приветственное сообщение'

    def groups_display(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    groups_display.short_description = 'Группы'
    


# Регистрируем модель и админ-класс
admin.site.register(FunctionalModule, FunctionalModuleAdmin)

# Перерегистрируем User и Group с новой конфигурацией
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

