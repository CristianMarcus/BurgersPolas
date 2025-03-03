from django import forms
from django.core.exceptions import ValidationError
from .models import Pedido, ClienteAnonimo, Cliente, ItemPedido, Producto
import re  # Importar el módulo para expresiones regulares

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['direccion', 'telefono']

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not telefono:
            raise ValidationError("El teléfono es obligatorio.")
        if not re.match(r'^\+?1?\d{9,15}$', telefono):
            raise ValidationError("El teléfono debe tener un formato válido.")
        return telefono

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['direccion','metodo_pago', 'comprobante_pago']

    def clean_direccion(self):
        direccion = self.cleaned_data['direccion']
        if not direccion:
            raise ValidationError("La dirección es obligatoria.")
        return direccion
    
    def clean_metodo_pago(self):
        metodo_pago = self.cleaned_data['metodo_pago']
        if not metodo_pago:
            raise forms.ValidationError("El método de pago es obligatorio.")
        return metodo_pago
    
class ClienteAnonimoForm(forms.ModelForm):
    class Meta:
        model = ClienteAnonimo
        fields = ['nombre', 'apellido', 'telefono']

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if not nombre:
            raise ValidationError("El nombre es obligatorio.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data['apellido']
        if not apellido:
            raise ValidationError("El apellido es obligatorio.")
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        if not telefono:
            raise ValidationError("El teléfono es obligatorio.")
        if not re.match(r'^\+?1?\d{9,15}$', telefono):
            raise ValidationError("El teléfono debe tener un formato válido.")
        return telefono

class ItemPedidoForm(forms.ModelForm):
    class Meta:
        model = ItemPedido
        fields = ['producto', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['producto'].queryset = Producto.objects.all()

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        return cantidad

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'imagen']

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise ValidationError("El precio debe ser mayor que cero.")
        return precio
    
    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('metodo_pago')
        comprobante_pago = cleaned_data.get('comprobante_pago')

        if metodo_pago == 'mercado_pago' and not comprobante_pago:
            self.add_error('comprobante_pago', "El comprobante de pago es obligatorio para Mercado Pago.")

        return cleaned_data