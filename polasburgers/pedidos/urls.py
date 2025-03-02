from django.urls import path
from . import views

urlpatterns = [
    # URLs para Productos
    path('productos/', views.lista_productos, name='listar_productos'),  # Lista todos los productos
    path('productos/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),  # Detalle de un producto específico
    path('agregar/', views.agregar_producto, name='agregar_producto'),  # Formulario para agregar un nuevo producto
    path('editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),  # Formulario para editar un producto existente
    path('eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),  # Confirmación para eliminar un producto

    # URLs para Pedidos
    path('crear/', views.crear_pedido, name='crear_pedido'),  # Formulario para crear un nuevo pedido
    path('pedidos/', views.listar_pedidos, name='listar_pedidos'),  # Lista todos los pedidos
    path('pedidos/<int:pedido_id>/', views.detalle_pedido, name='detalle_pedido'),  # Detalle de un pedido específico
    path('eliminar_pedido/<int:pedido_id>/', views.eliminar_pedido, name='eliminar_pedido'),  # Confirmación para eliminar un pedido

    # URLs para el Carrito de Compras
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),  # Agrega un producto al carrito
    path('ver_carrito/', views.ver_carrito, name='ver_carrito'),  # Muestra el contenido del carrito
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),  # Actualiza la cantidad de un producto en el carrito
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),  # Elimina un producto del carrito
    path('carrito/vaciar/', views.vaciar_carrito, name='vaciar_carrito'),  # Vacía todo el carrito
]