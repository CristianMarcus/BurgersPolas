from django.urls import path
from . import views

urlpatterns = [
    
    path('productos/', views.lista_productos, name='lista_productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('pedido/crear/', views.crear_pedido, name='crear_pedido'),
]