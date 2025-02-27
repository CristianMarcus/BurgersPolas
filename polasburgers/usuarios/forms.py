from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import PerfilUsuario
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

class RegistroForm(forms.Form):
    username = forms.CharField(max_length=150, label="Usuario")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirmar Contraseña")

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya está registrado.")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        validate_password(password)  # Usa los validadores de Django
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        user = User.objects.create_user(username=username, email=email, password=password)
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    class Meta:
        model = User
        fields = ("username", "password")

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ('nombre', 'apellidos', 'telefono', 'direccion')