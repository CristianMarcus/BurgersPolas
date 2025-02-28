from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Pedido, ItemPedido, Cliente, ClienteAnonimo
from .forms import PedidoForm, ItemPedidoForm, ProductoForm, ClienteAnonimoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES) # request.FILES para manejar imágenes
        if form.is_valid():
            form.save()
            messages.success(request, "Producto agregado exitosamente.")
            return redirect('lista_productos') # Redirige a la lista de productos
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = ProductoForm()
        print(form)
    return render(request, 'pedidos/agregar_producto.html', {'form': form})


@login_required
def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto editado exitosamente.")
            return redirect('lista_productos')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'pedidos/editar_producto.html', {'form': form, 'producto': producto})

@login_required
def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "Producto eliminado exitosamente.")
        return redirect('lista_productos')
    return render(request, 'pedidos/eliminar_producto.html', {'producto': producto})


def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'pedidos/lista_productos.html', {'productos': productos})


def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, 'pedidos/detalle_producto.html', {'producto': producto})



def crear_pedido(request):
    if request.method == 'POST':
        cliente_form = ClienteAnonimoForm(request.POST)
        item_form = ItemPedidoForm(request.POST)
        if cliente_form.is_valid() and item_form.is_valid():
            cliente_anonimo = cliente_form.save()
            request.session['cliente_anonimo_id'] = cliente_anonimo.id
            pedido = Pedido.objects.create(cliente_anonimo=cliente_anonimo)  # Crea el pedido aquí
            item = item_form.save(commit=False)
            item.pedido = pedido
            item.precio_unitario = item.producto.precio
            item.save()
            pedido.total = sum(item.precio_unitario * item.cantidad for item in ItemPedido.objects.filter(pedido=pedido))
            pedido.save()
            messages.success(request, "Pedido creado exitosamente.")
            return redirect('detalle_pedido', pedido_id=pedido.id)
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        cliente_form = ClienteAnonimoForm()
        item_form = ItemPedidoForm()
    return render(request, 'pedidos/crear_pedido.html', {'cliente_form': cliente_form, 'item_form': item_form})

def listar_pedidos(request):
    if request.user.is_authenticated:
        cliente, created = Cliente.objects.get_or_create(user=request.user)
        pedidos = Pedido.objects.filter(cliente=cliente)
    else:
        cliente_anonimo_id = request.session.get('cliente_anonimo_id')
        if cliente_anonimo_id:
            pedidos = Pedido.objects.filter(cliente_anonimo_id=cliente_anonimo_id)
        else:
            pedidos = []
    return render(request, 'pedidos/listar_pedidos.html', {'pedidos': pedidos})


def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.user.is_authenticated:
        if pedido.cliente and pedido.cliente.user == request.user:
            return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido})
    else:
        cliente_anonimo_id = request.session.get('cliente_anonimo_id')
        if cliente_anonimo_id and pedido.cliente_anonimo_id == cliente_anonimo_id:
            return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido})
    messages.error(request, "No tienes permiso para ver este pedido.")
    return redirect('listar_pedidos')

def eliminar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id)
    if request.user.is_authenticated:
        if pedido.cliente and pedido.cliente.user == request.user:
            pedido.delete()
            messages.success(request, "Pedido eliminado exitosamente.")
            return redirect('listar_pedidos')
    else:
        cliente_anonimo_id = request.session.get('cliente_anonimo_id')
        if cliente_anonimo_id and pedido.cliente_anonimo_id == cliente_anonimo_id:
            pedido.delete()
            messages.success(request, "Pedido eliminado exitosamente.")
            return redirect('listar_pedidos')
    messages.error(request, "No tienes permiso para eliminar este pedido.")
    return redirect('listar_pedidos')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
from django.contrib import messages

def agregar_al_carrito(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id) # Convertir a string para usarlo como clave

    if producto_id_str in carrito:
        carrito[producto_id_str]['cantidad'] += 1
    else:
        carrito[producto_id_str] = {
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'cantidad': 1,
        }

    request.session['carrito'] = carrito
    messages.success(request, f'{producto.nombre} agregado al carrito.')
    return redirect('listar_productos') # Redirige a la lista de productos

# Vistas para el carrito

def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    productos_carrito = []
    total = 0

    for producto_id, detalles in carrito.items():
        subtotal = float(detalles['precio']) * detalles['cantidad']
        detalles['subtotal'] = subtotal
        detalles['id'] = producto_id
        productos_carrito.append(detalles)
        total += subtotal

    return render(request, 'pedidos/carrito.html', {
        'productos_carrito': productos_carrito,
        'total': total,
    })

def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    producto_id_str = str(producto_id)

    if producto_id_str in carrito:
        del carrito[producto_id_str]
        request.session['carrito'] = carrito
        messages.success(request, 'Producto eliminado del carrito.')

    return redirect('ver_carrito')