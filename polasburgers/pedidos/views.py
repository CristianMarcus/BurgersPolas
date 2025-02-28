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


from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Pedido, ItemPedido, Cliente, ClienteAnonimo
from .forms import PedidoForm, ItemPedidoForm, ProductoForm, ClienteAnonimoForm
from django.contrib import messages

def crear_pedido(request):
    if request.method == 'POST':
        cliente_form = ClienteAnonimoForm(request.POST)
        pedido_form = PedidoForm(request.POST)
        item_form = ItemPedidoForm(request.POST)
        if cliente_form.is_valid() and pedido_form.is_valid() and item_form.is_valid():
            cliente_anonimo = cliente_form.save()
            request.session['cliente_anonimo_id'] = cliente_anonimo.id  # Almacena el ID en la sesión
            pedido = pedido_form.save(commit=False)
            pedido.cliente_anonimo = cliente_anonimo
            pedido.save()
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
        pedido_form = PedidoForm()
        item_form = ItemPedidoForm()
    return render(request, 'pedidos/crear_pedido.html', {'cliente_form': cliente_form, 'pedido_form': pedido_form, 'item_form': item_form})

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
    pedido = get_object_or_404(Pedido, pk=pedido_id, cliente__user=request.user)
    items = ItemPedido.objects.filter(pedido=pedido)
    return render(request, 'pedidos/detalle_pedido.html', {'pedido': pedido, 'items': items})