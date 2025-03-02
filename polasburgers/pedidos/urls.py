from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.lista_productos, name='listar_productos'), # cambia pedido/ a productos/
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'), #cambia pedido/ a productos/
    path('crear/', views.crear_pedido, name='crear_pedido'), #cambia pedido/crear a crear/
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'), # cambia pedido/ a pedidos/
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'), # cambia pedido/ a pedidos/
    path('eliminar_pedido/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),
    path('agregar/', views.agregar_producto, name='agregar_producto'),
    path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('eliminar_del_carrito/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
]