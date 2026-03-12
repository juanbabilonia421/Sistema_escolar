# comercial/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def solo_coordinador(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if not request.user.es_coordinador():
            messages.error(request, 'Solo el coordinador puede acceder a esta sección.')
            return redirect('usuarios:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def coordinador_o_acudiente(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if not (request.user.es_coordinador() or request.user.es_acudiente()):
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('usuarios:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper