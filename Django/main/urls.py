from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from django.contrib import admin
from app import views
 
urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('logout/', views.user_logout, name='logout'),
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('chat/<str:app_slug>/', views.chat_view, name='chat'),
    path('download/<str:file_name>/', views.download_file_view, name='download_file'),
    path('upload/', views.file_upload, name='file_upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)