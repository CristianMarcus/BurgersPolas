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


def actualizar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    if request.method == 'POST':
        try:
            nueva_cantidad = int(request.POST.get('cantidad', 1))
        except ValueError:
            nueva_cantidad = 1

        producto.cantidad = nueva_cantidad
        producto.save()  # Esto recalcula el subtotal automáticamente
        messages.success(request, "Producto actualizado correctamente.")
        return redirect('vista_carrito')  # Asegúrate de redirigir a la vista del carrito o lista de productos
    else:
        messages.error(request, "Método no permitido.")
        return redirect('vista_carrito')


def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'pedidos/lista_productos.html', {'productos': productos})

def detalle_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    return render(request, 'pedidos/detalle_producto.html', {'producto': producto})




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Pedido, ItemPedido, ClienteAnonimo, Producto
from .forms import PedidoForm, ClienteAnonimoForm
from django.utils import timezone  # Importa timezone

def crear_pedido(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.error(request, 'El carrito está vacío.')
        return redirect('listar_productos')

    if request.method == 'POST':
        form = PedidoForm(request.POST, request.FILES)
        cliente_anonimo_form = ClienteAnonimoForm(request.POST)

        if form.is_valid() and cliente_anonimo_form.is_valid():
            try:
                cliente_anonimo = cliente_anonimo_form.save()
                pedido = form.save(commit=False)
                pedido.cliente_anonimo = cliente_anonimo
                pedido.fecha_pedido = timezone.now()  # Establece la fecha y hora del pedido
                pedido.save()

                total = 0  # Inicializa el total del pedido
                for producto_id, detalles in carrito.items():
                    producto = get_object_or_404(Producto, pk=producto_id)
                    cantidad = detalles['cantidad']
                    precio_unitario = producto.precio
                    subtotal = cantidad * precio_unitario
                    total += subtotal
                    ItemPedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad, precio_unitario=precio_unitario)

                pedido.total = total  # Establece el total del pedido
                pedido.save()

                del request.session['carrito']
                messages.success(request, 'Pedido creado con éxito.')
                return redirect('listar_pedidos')
            except Exception as e:
                messages.error(request, f'Error al crear el pedido: {e}')
        else:
            messages.error(request, 'Error en el formulario.')
    else:
        form = PedidoForm()
        cliente_anonimo_form = ClienteAnonimoForm()

    return render(request, 'pedidos/crear_pedido.html', {'form': form, 'cliente_anonimo_form': cliente_anonimo_form})


def enviar_mensaje_whatsapp(request, pedido):
    numero_telefono = "+5491126884940"
    mensaje = f"Nuevo pedido #{pedido.id}:\n"
    for item in pedido.itempedido_set.all():
        mensaje += f"- {item.producto.nombre} x {item.cantidad}\n"
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
        carrito = request.session.get('carrito', {})  # Obtiene el carrito desde la sesión
        producto_id = str(producto_id)  # Convierte el ID del producto a string para que coincida con las claves del carrito

        if producto_id in carrito:
            try:
                nueva_cantidad = int(request.POST.get('cantidad', 1))  # Obtiene la cantidad del formulario
                if nueva_cantidad < 1:
                    nueva_cantidad = 1  # Evita valores negativos o 0
                
                carrito[producto_id]['cantidad'] = nueva_cantidad  # Actualiza la cantidad
                carrito[producto_id]['subtotal'] = float(carrito[producto_id]['precio']) * nueva_cantidad  # Recalcula el subtotal

                request.session['carrito'] = carrito
                request.session.modified = True
                request.session.save()

                messages.success(request, "Cantidad actualizada correctamente.")
            except ValueError:
                messages.error(request, "La cantidad ingresada no es válida.")
        else:
            messages.error(request, "El producto no se encontró en el carrito.")

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
    pedido = get_object_or_404(Pedido, id=pedido_id)
    items = ItemPedido.objects.filter(pedido=pedido)  # Obtiene los items del pedido

    return render(request, 'pedidos/detalle_pedido.html', {
        'pedido': pedido,
        'items': items  # Pasar los items al template
    })


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
        productos_carrito = []
        total = 0

        for producto_id, detalles in carrito.items():
            try:
                precio = float(detalles['precio'])
                cantidad = detalles['cantidad']
                subtotal = precio * cantidad
                detalles['subtotal'] = subtotal
                detalles['id'] = producto_id
                productos_carrito.append(detalles)
                total += subtotal
            except ValueError:
                messages.error(request, f"Error: Precio inválido para {detalles['nombre']}.")

        return render(request, 'pedidos/carrito.html', {
            'productos_carrito': productos_carrito,
            'total': total
        })
    except Exception as e:
        messages.error(request, f'Error al ver el carrito: {e}')
        return redirect('listar_productos')
