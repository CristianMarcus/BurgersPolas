from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Importa las vistas de autenticación de Django

urlpatterns = [
    path('register/', views.registro_view, name='register'),
    path('login/', views.login_view, name='login'), # Usa tu vista login_view personalizada
    path('logout/', views.logout_view, name='logout'), # Usa tu vista logout_view personalizada
    path('perfil/', views.perfil_view, name='perfil'),
]