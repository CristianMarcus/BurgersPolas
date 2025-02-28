from django import forms
from .models import Pedido, ClienteAnonimo, Cliente, ItemPedido, Producto
from django.core.exceptions import ValidationError

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['direccion', 'telefono']

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = []

class ClienteAnonimoForm(forms.ModelForm):
    class Meta:
        model = ClienteAnonimo
        fields = ['nombre', 'direccion', 'telefono']

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
        fields = '__all__'