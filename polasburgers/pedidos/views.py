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




from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Pedido, ItemPedido, ClienteAnonimo
from django.utils.timezone import now

def crear_pedido(request):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})

        if not carrito:
            messages.error(request, "El carrito está vacío.")
            return redirect('ver_carrito')

        # Verificar si el usuario está autenticado o es un cliente anónimo
        if request.user.is_authenticated:
            cliente = request.user.cliente  # Relación OneToOne
            cliente_anonimo = None
        else:
            # Obtener datos de un formulario para cliente anónimo
            nombre = request.POST.get('nombre')
            apellido = request.POST.get('apellido', 'invitado')
            telefono = request.POST.get('telefono')
            
            if not nombre or not telefono:
                messages.error(request, "Debe proporcionar un nombre y teléfono para continuar.")
                return redirect('ver_carrito')
            
            cliente_anonimo, _ = ClienteAnonimo.objects.get_or_create(
                nombre=nombre, apellido=apellido, telefono=telefono
            )
            cliente = None

        metodo_pago = request.POST.get('metodo_pago', 'efectivo')
        direccion = request.POST.get('direccion', 'Sin dirección')

        # Crear pedido en la BD
        pedido = Pedido.objects.create(
            direccion=direccion,
            cliente=cliente,
            cliente_anonimo=cliente_anonimo,
            fecha_pedido=now(),
            metodo_pago=metodo_pago,
            total=0  # Se actualizará más adelante
        )

        total_pedido = 0
        for producto_id, item in carrito.items():
            cantidad = int(item['cantidad'])
            precio_unitario = float(item['precio'])
            total_pedido += cantidad * precio_unitario

            ItemPedido.objects.create(
                pedido=pedido,
                producto_id=producto_id,
                cantidad=cantidad,
                precio_unitario=precio_unitario
            )

        # Actualizar el total del pedido
        pedido.total = total_pedido
        pedido.save()

        # Vaciar el carrito de la sesión
        request.session['carrito'] = {}
        messages.success(request, "Pedido realizado con éxito.")
        return redirect('listar_pedidos')

    return render(request, 'pedidos/crear_pedido.html')


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

                request.session['carrito'] = carrito  # Guarda los cambios en la sesión
                request.session.modified = True  # Asegura que Django guarde la sesión modificada

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
        print(f"Carrito en ver_carrito: {carrito}")
        productos_carrito = []
        total = 0

        for producto_id, detalles in carrito.items():
            try:
                precio = float(detalles['precio'])
                cantidad = int(detalles['cantidad'])
                print(f"Cantidad en ver_carrito: {cantidad}")
                # Recalcula siempre el subtotal basado en la cantidad actualizada
                detalles['subtotal'] = precio * cantidad
                detalles['id'] = producto_id
                productos_carrito.append(detalles)
                total += detalles['subtotal']
            except ValueError:
                error_msg = f"Error: No se pudo convertir el precio '{detalles['precio']}' o la cantidad '{detalles['cantidad']}' a un número."
                print(error_msg)
                messages.error(request, error_msg)

        return render(request, 'pedidos/carrito.html', {
            'productos_carrito': productos_carrito,
            'total': total
        })
    except Exception as e:
        print(f"Error en ver_carrito: {e}")
        messages.error(request, f'Error al ver el carrito: {e}')
        return redirect('listar_productos')
