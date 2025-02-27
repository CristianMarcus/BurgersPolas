from django import forms
from .models import Pedido, Cliente
from django.contrib.auth.models import User

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['direccion', 'telefono']

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.all()