from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100, blank=True)
    apellidos = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(
        max_length=15,
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="El número de teléfono debe ingresarse en el formato: '+999999999'. Se permiten hasta 15 dígitos.",
            ),
        ],
    )
    direccion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.user.username