from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.user.username

class Pedido(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('preparacion', 'En Preparación'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    )
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Pedido de {self.cliente.user.username} - {self.fecha_pedido}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en el pedido {self.pedido.id}"