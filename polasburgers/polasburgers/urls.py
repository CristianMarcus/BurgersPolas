from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from pedidos import views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('usuarios.urls')),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('', include('pedidos.urls')),
    path('productos/', include('productos.urls')),
    
]