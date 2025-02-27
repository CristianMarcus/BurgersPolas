from django.shortcuts import render, redirect
from .models import Producto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import UserForm, ClienteForm, PedidoForm

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'pedidos/lista_productos.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = Producto.objects.get(pk=producto_id)
    return render(request, 'pedidos/detalle_producto.html', {'producto': producto})

def crear_pedido(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        cliente_form = ClienteForm(request.POST)
        pedido_form = PedidoForm(request.POST)

        if user_form.is_valid() and cliente_form.is_valid() and pedido_form.is_valid():
            user = user_form.save()
            user.set_password(user.cleaned_data['password'])
            user.save()

            cliente = cliente_form.save(commit=False)
            cliente.user = user
            cliente.save()

            pedido = pedido_form.save(commit=False)
            pedido.cliente = cliente
            pedido.save()

            login(request, user)

            return redirect('lista_productos')
    else:
        user_form = UserForm()
        cliente_form = ClienteForm()
        pedido_form = PedidoForm()

    return render(request, 'pedidos/crear_pedido.html', {
        'user_form': user_form,
        'cliente_form': cliente_form,
        'pedido_form': pedido_form,
    })

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('lista_productos')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})    