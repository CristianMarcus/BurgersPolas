from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm, PerfilUsuarioForm
from .models import PerfilUsuario
from django.contrib import messages





def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            PerfilUsuario.objects.create(user=user)  # Crea el PerfilUsuario aquí
            messages.success(request, "Registro exitoso. ¡Bienvenido!")
            return redirect('perfil')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = RegistroForm()
    return render(request, 'usuarios/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('perfil')  # Redirige al perfil
    else:
        form = AuthenticationForm()
    return render(request, 'usuarios/login.html', {'form': form})


@login_required
def perfil_view(request):
    perfil, created = PerfilUsuario.objects.get_or_create(user=request.user) # Usar get_or_create

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado exitosamente.")
            return redirect('perfil')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = PerfilUsuarioForm(instance=perfil)

    return render(request, 'usuarios/perfil.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')  # Redirige a la página principal