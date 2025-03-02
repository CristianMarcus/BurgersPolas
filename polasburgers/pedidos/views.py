from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Pedido, ItemPedido, Cliente, ClienteAnonimo
from .forms import PedidoForm, ItemPedidoForm, ProductoForm, ClienteAnonimoForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
import uuid
import pywhatkit  # Importar la librería para WhatsApp


def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto agregado exitosamente.")
                return redirect('lista_productos')
            except Exception as e:
                messages.error(request, f"Error al agregar el producto: {e}")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = ProductoForm()
    return render(request, 'pedidos/agregar_producto.html', {'form': form})


def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Producto editado exitosamente.")
                return redirect('lista_productos')
            except Exception as e:
                messages.error(request, f"Error al editar el producto: {e}")
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'pedidos/editar_producto.html', {'form': form, 'producto': producto})


def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == 'POST':
        try:
            producto.delete()
            messages.success(request, "Producto eliminado exitosamente.")
            return redirect('lista_productos')
        except Exception as e:
            messages.error(request, f"Error al eliminar el producto: {e}")
    return render(request, 'pedidos/eliminar_producto.html', {'producto': producto})

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'pedidos/lista_productos.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, 'pedidos/detalle_producto.html', {'producto': producto})


def crear_pedido(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'El carrito está vacío. Agrega productos antes de crear un pedido.')
        return redirect('listar_productos')

    if request.method == 'POST':
        form = PedidoForm(request.POST)
        cliente_anonimo_form = ClienteAnonimoForm(request.POST)
        if form.is_valid() and cliente_anonimo_form.is_valid():
            print("Formularios válidos")  # agregue esto.
            try:
                cliente_anonimo = cliente_anonimo_form.save()
                pedido = form.save(commit=False)
                pedido.cliente_anonimo = cliente_anonimo
                pedido.save()

                for producto_id, detalles in carrito.items():
                    producto = get_object_or_404(Producto, pk=producto_id)
                    # Agrega esta línea para obtener el precio unitario
                    precio_unitario = producto.precio
                    ItemPedido.objects.create(pedido=pedido, producto=producto, cantidad=detalles['cantidad'], precio_unitario=precio_unitario)

                del request.session['carrito']
                messages.success(request, 'Pedido creado con éxito.')
                enviar_mensaje_whatsapp(request, pedido)
                return redirect('detalle_pedido', pedido_id=pedido.id)
            except Exception as e:
                print(f"Error al crear el pedido: {e}")  # agregue esto.
                messages.error(request, f'Error al crear el pedido: {e}')
        else:
            print(form.errors)  # agregue esto.
            print(cliente_anonimo_form.errors)  # agregue esto.
            messages.error(request, 'Error en el formulario. Por favor, corrige los errores.')
    else:
        form = PedidoForm()
        cliente_anonimo_form = ClienteAnonimoForm()

    return render(request, 'pedidos/crear_pedido.html', {'form': form, 'cliente_anonimo_form': cliente_anonimo_form})

def enviar_mensaje_whatsapp(request, pedido):
        numero_telefono = "+5491126884940"
        mensaje = f"Nuevo pedido #{pedido.id}:\n"
        for item in pedido.itempedido_set.all():
            mensaje += f"- {item.producto.nombre} x {item.cantidad}\n"
        # Modifica esta línea
        total = sum(float(item.producto.precio) * item.cantidad for item in pedido.itempedido_set.all())
        mensaje += f"Total: ${total}\n"
        mensaje += f"Cliente: {pedido.cliente_anonimo.nombre} {pedido.cliente_anonimo.apellido}\n"
        mensaje += f"Teléfono: {pedido.cliente_anonimo.telefono}\n"
        mensaje += f"Dirección: {pedido.direccion}\n"
        mensaje += "Pago: Efectivo o Mercado Pago (alias/CBU: pola7188)"

        try:
            pywhatkit.sendwhatmsg_instantly(numero_telefono, mensaje)
            messages.success(request, "Mensaje de WhatsApp enviado.")
        except Exception as e:
            messages.error(request, f"Error al enviar mensaje de WhatsApp: {e}")
        
def actualizar_cantidad(request, producto_id):
        if request.method == 'POST':
            cantidad = request.POST.get('cantidad')
            if cantidad and cantidad.isdigit() and int(cantidad) > 0:
                cantidad = int(cantidad)
                carrito = request.session.get('carrito', {})
                if producto_id in carrito:
                    carrito[producto_id]['cantidad'] = cantidad
                    # Recalcula el subtotal
                    precio = float(carrito[producto_id]['precio'])
                    carrito[producto_id]['subtotal'] = precio * cantidad
                    request.session['carrito'] = carrito
            else:
                messages.error(request, 'Por favor, ingresa una cantidad válida.')
        return redirect('ver_carrito')

def eliminar_del_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    try:
        if producto_id in carrito:
            del carrito[producto_id]
            request.session['carrito'] = carrito
            messages.success(request, 'Producto eliminado del carrito.')
        else:
            messages.error(request, 'El producto no está en el carrito.')
    except Exception as e:
        messages.error(request, f'Error al eliminar el producto del carrito: {e}')

    return redirect('ver_carrito')

def vaciar_carrito(request):
    if 'carrito' in request.session:
        del request.session['carrito']
    return redirect('ver_carrito')

def listar_pedidos(request):
    try:
        if request.user.is_authenticated:
            pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('productos')
        else:
            pedidos = []
            for key in request.session.keys():
                if key.startswith('pedido_'):
                    identificador_pedido = key.split('_')[1]
                    try:
                        pedido = Pedido.objects.get(identificador_pedido=identificador_pedido).prefetch_related('productos')
                        pedidos.append(pedido)
                    except Pedido.DoesNotExist:
                        pass
        return render(request, 'pedidos/listar_pedidos.html', {'pedidos': pedidos})
    except Exception as e:
        messages.error(request, f'Error al listar los pedidos: {e}')
        return render(request, 'pedidos/listar_pedidos.html', {'pedidos': []})

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
    try:
        if request.user.is_authenticated:
            pedido = get_object_or_404(Pedido, pk=pedido_id, usuario=request.user)
        else:
            pedido = get_object_or_404(Pedido, pk=pedido_id)

        if request.method == 'POST':
            if not request.user.is_authenticated:
                del request.session[f'pedido_{pedido.identificador_pedido}']
            pedido.delete()
            messages.success(request, 'Pedido eliminado con éxito.')
            return redirect('listar_pedidos')
        return render(request, 'pedidos/eliminar_pedido.html', {'pedido': pedido})
    except Pedido.DoesNotExist:
        messages.error(request, 'El pedido no existe.')
        return redirect('listar_pedidos')
    except Exception as e:
        messages.error(request, f'Error al eliminar el pedido: {e}')
        return redirect('listar_pedidos')

def agregar_al_carrito(request, producto_id):
        try:
            producto = get_object_or_404(Producto, pk=producto_id)
            carrito = request.session.get('carrito', {})

            if producto_id in carrito:
                carrito[producto_id]['cantidad'] += 1
            else:
                carrito[producto_id] = {
                    'nombre': producto.nombre,
                    'precio': str(producto.precio),
                    'cantidad': 1,
                }

            request.session['carrito'] = carrito
            messages.success(request, f'{producto.nombre} agregado al carrito.')
        except Producto.DoesNotExist:
            messages.error(request, 'El producto no existe.')
        except Exception as e:
            messages.error(request, f'Error al agregar el producto al carrito: {e}')
        return redirect('ver_carrito')

def eliminar_del_carrito(request, producto_id):
        carrito = request.session.get('carrito', {})
        try:
            if producto_id in carrito:
                del carrito[producto_id]
                request.session['carrito'] = carrito
                messages.success(request, 'Producto eliminado del carrito.')
            else:
                messages.error(request, 'El producto no está en el carrito.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el producto del carrito: {e}')

        return redirect('ver_carrito')

def ver_carrito(request):
        try:
            carrito = request.session.get('carrito', {})
            print(f"Carrito en ver_carrito: {carrito}") # Agregue esta linea
            productos_carrito = []
            total = 0

            for producto_id, detalles in carrito.items():
                try:
                    precio = float(detalles['precio'])
                    cantidad = detalles['cantidad']
                    print(f"Cantidad en ver_carrito: {cantidad}") # Agregue esta linea
                    subtotal = precio * cantidad
                    detalles['subtotal'] = subtotal
                    detalles['id'] = producto_id
                    productos_carrito.append(detalles)
                    total += subtotal
                except ValueError:
                    print(f"Error: No se pudo convertir el precio '{detalles['precio']}' a un número.")
                    messages.error(request, f"Error: No se pudo convertir el precio '{detalles['precio']}' a un número.")

            return render(request, 'pedidos/carrito.html', {
                'productos_carrito': productos_carrito,
                'total': total
            })
        except Exception as e:
            print(f"Error en ver_carrito: {e}")
            messages.error(request, f'Error al ver el carrito: {e}')
            return redirect('listar_productos')