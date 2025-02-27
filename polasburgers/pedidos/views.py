from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Pedido, ItemPedido, Cliente
from .forms import PedidoForm, ItemPedidoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'pedidos/lista_productos.html', {'productos': productos})

@login_required
def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, 'pedidos/detalle_producto.html', {'producto': producto})

@login_required
def crear_pedido(request):
    cliente, created = Cliente.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        pedido_form = PedidoForm(request.POST)
        item_form = ItemPedidoForm(request.POST)
        if pedido_form.is_valid() and item_form.is_valid():
            try:
                pedido = Pedido.objects.create(cliente=cliente)
                item = item_form.save(commit=False)
                item.pedido = pedido
                item.precio_unitario = item.producto.precio
                item.save()
                pedido.total = sum(item.precio_unitario * item.cantidad for item in ItemPedido.objects.filter(pedido=pedido))
                pedido.save()
                messages.success(request, "Pedido creado exitosamente.")
                return redirect('detalle_pedido', pedido_id=pedido.id)
            except Exception as e:
                messages.error(request, f"Error al crear el pedido: {e}")
                return redirect('crear_pedido')
    else:
        pedido_form = PedidoForm()
        item_form = ItemPedidoForm()
    return render(request, 'pedidos/crear_pedido.html', {'pedido_form': pedido_form, 'item_form': item_form})

@login_required
def listar_pedidos(request):
    cliente, created = Cliente.objects.get_or_create(user=request.user) # Cambia usuario a user
    pedidos = Pedido.objects.filter(cliente=cliente)
    return render(request, 'pedidos/listar_pedidos.html', {'pedidos': pedidos})

@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, pk=pedido_id, cliente__user=request.user)
    items = ItemPedido.objects.filter(pedido=pedido)
    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido, 'items': items})