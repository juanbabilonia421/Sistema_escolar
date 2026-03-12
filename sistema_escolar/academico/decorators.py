# academico/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def solo_coordinador(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if not request.user.es_coordinador():
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('usuarios:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def coordinador_o_profesor(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if not (request.user.es_coordinador() or request.user.es_profesor()):
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('usuarios:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def solo_estudiante(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if not request.user.es_estudiante():
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('usuarios:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def solo_acudiente(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if not request.user.es_acudiente():
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('usuarios:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def no_estudiante(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if request.user.es_estudiante():
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('usuarios:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper