from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.lista_productos, name='lista_productos'), # cambia pedido/ a productos/
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'), #cambia pedido/ a productos/
    path('crear/', views.crear_pedido, name='crear_pedido'), #cambia pedido/crear a crear/
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'), # cambia pedido/ a pedidos/
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'), # cambia pedido/ a pedidos/
]