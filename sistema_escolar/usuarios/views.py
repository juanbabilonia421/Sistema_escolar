# usuarios/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from .models import Usuario, Estudiante, Profesor, Acudiente
from .forms  import UsuarioForm, EstudianteForm, ProfesorForm, AcudienteForm
from .decorators import solo_coordinador


# ─────────────────────────────────────────
# AUTENTICACIÓN
# ─────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('usuarios:dashboard')

        return render(request, 'usuarios/login.html', {'error': True})

    return render(request, 'usuarios/login.html')


def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


@login_required
def dashboard_view(request):
    user    = request.user
    context = {'today': timezone.now()}

    if user.es_coordinador():
        from academico.models import Curso, Asignacion, Nota, Asistencia, Actividad
        from comercial.models import Cotizacion

        cursos_data = []
        for curso in Curso.objects.all():
            cursos_data.append({
                'curso':             curso,
                'total_estudiantes': curso.estudiantes.count(),
                'total_materias':    curso.asignaciones.values('materia').distinct().count(),
            })

        context.update({
            'total_cursos':       Curso.objects.count(),
            'total_profesores':   Profesor.objects.count(),
            'total_estudiantes':  Estudiante.objects.count(),
            'total_cotizaciones': Cotizacion.objects.count(),
            'total_asignaciones': Asignacion.objects.count(),
            'total_notas':        Nota.objects.count(),
            'total_asistencias':  Asistencia.objects.count(),
            'total_actividades':  Actividad.objects.count(),
            'cursos_data':        cursos_data,
        })

    elif user.es_profesor():
        from academico.models import Asignacion
        profesor = Profesor.objects.filter(usuario=user).first()
        if profesor:
            context['mis_asignaciones'] = Asignacion.objects.filter(
                profesor=profesor
            ).select_related('materia', 'curso')
        else:
            context['mis_asignaciones'] = []

    elif user.es_estudiante():
        from academico.models import Nota
        estudiante = Estudiante.objects.filter(usuario=user).first()
        if estudiante:
            context['mis_notas'] = Nota.objects.filter(
                estudiante=estudiante
            ).select_related('asignacion__materia').order_by('-id')[:10]
        else:
            context['mis_notas'] = []

    elif user.es_acudiente():
        acudiente = Acudiente.objects.filter(usuario=user).first()
        if acudiente:
            context['mis_estudiantes'] = acudiente.estudiantes.select_related(
                'usuario', 'curso'
            ).all()
        else:
            context['mis_estudiantes'] = []

    return render(request, 'usuarios/dashboard.html', context)


# ─────────────────────────────────────────
# GESTIÓN DE USUARIOS (solo coordinador)
# ─────────────────────────────────────────

@login_required
@solo_coordinador
def lista_usuarios(request):
    usuarios = Usuario.objects.all().order_by('rol', 'last_name')

    busqueda = request.GET.get('q', '')
    rol      = request.GET.get('rol', '')
    estado   = request.GET.get('estado', '')

    if busqueda:
        usuarios = usuarios.filter(
            models.Q(first_name__icontains=busqueda) |
            models.Q(last_name__icontains=busqueda)  |
            models.Q(username__icontains=busqueda)   |
            models.Q(email__icontains=busqueda)
        )
    if rol:
        usuarios = usuarios.filter(rol=rol)
    if estado == 'activo':
        usuarios = usuarios.filter(is_active=True)
    elif estado == 'inactivo':
        usuarios = usuarios.filter(is_active=False)

    return render(request, 'usuarios/lista_usuarios.html', {
        'usuarios': usuarios,
        'busqueda': busqueda,
        'rol':      rol,
        'estado':   estado,
        'roles':    Usuario.Rol.choices,
    })


@login_required
@solo_coordinador
def crear_usuario(request):
    form = UsuarioForm(request.POST or None)
    if form.is_valid():
        usuario = form.save()
        messages.success(request, f'Usuario {usuario.username} creado.')

        if usuario.rol == Usuario.Rol.ESTUDIANTE:
            return redirect('usuarios:crear_perfil_estudiante', pk=usuario.pk)
        elif usuario.rol == Usuario.Rol.PROFESOR:
            return redirect('usuarios:crear_perfil_profesor', pk=usuario.pk)
        elif usuario.rol == Usuario.Rol.ACUDIENTE:
            return redirect('usuarios:crear_perfil_acudiente', pk=usuario.pk)
        else:
            return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/form_usuario.html', {
        'form':   form,
        'titulo': 'Nuevo usuario',
    })


@login_required
@solo_coordinador
def crear_perfil_estudiante(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form    = EstudianteForm(request.POST or None)
    if form.is_valid():
        perfil         = form.save(commit=False)
        perfil.usuario = usuario
        perfil.save()
        messages.success(request, 'Perfil de estudiante creado.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/form_perfil.html', {
        'form':    form,
        'titulo':  f'Perfil estudiante: {usuario.get_full_name()}',
        'usuario': usuario,
    })


@login_required
@solo_coordinador
def crear_perfil_profesor(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form    = ProfesorForm(request.POST or None)
    if form.is_valid():
        perfil         = form.save(commit=False)
        perfil.usuario = usuario
        perfil.save()
        messages.success(request, 'Perfil de profesor creado.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/form_perfil.html', {
        'form':    form,
        'titulo':  f'Perfil profesor: {usuario.get_full_name()}',
        'usuario': usuario,
    })


@login_required
@solo_coordinador
def crear_perfil_acudiente(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    form    = AcudienteForm(request.POST or None)
    if form.is_valid():
        perfil         = form.save(commit=False)
        perfil.usuario = usuario
        perfil.save()
        form.save_m2m()
        messages.success(request, 'Perfil de acudiente creado.')
        return redirect('usuarios:lista_usuarios')
    return render(request, 'usuarios/form_perfil.html', {
        'form':    form,
        'titulo':  f'Perfil acudiente: {usuario.get_full_name()}',
        'usuario': usuario,
    })


@login_required
@solo_coordinador
def toggle_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.is_superuser:
        messages.error(request, 'No puedes desactivar al superusuario.')
        return redirect('usuarios:lista_usuarios')

    if usuario == request.user:
        messages.error(request, 'No puedes desactivarte a ti mismo.')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        usuario.is_active = not usuario.is_active
        usuario.save()
        estado = 'activado' if usuario.is_active else 'desactivado'
        messages.success(request, f'Usuario {usuario.get_full_name()} {estado} correctamente.')

    return redirect('usuarios:lista_usuarios')


@login_required
@solo_coordinador
def ver_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    perfil_estudiante = None
    perfil_profesor   = None
    perfil_acudiente  = None

    if usuario.rol == Usuario.Rol.ESTUDIANTE:
        perfil_estudiante = Estudiante.objects.filter(usuario=usuario).first()
    elif usuario.rol == Usuario.Rol.PROFESOR:
        perfil_profesor = Profesor.objects.filter(usuario=usuario).first()
    elif usuario.rol == Usuario.Rol.ACUDIENTE:
        perfil_acudiente = Acudiente.objects.filter(usuario=usuario).first()

    return render(request, 'usuarios/ver_usuario.html', {
        'u':                  usuario,
        'perfil_estudiante':  perfil_estudiante,
        'perfil_profesor':    perfil_profesor,
        'perfil_acudiente':   perfil_acudiente,
    })


@login_required
@solo_coordinador
def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.is_superuser:
        messages.error(request, 'No puedes editar al superusuario.')
        return redirect('usuarios:lista_usuarios')

    form = UsuarioForm(request.POST or None, instance=usuario)

    perfil_form = None
    if usuario.rol == Usuario.Rol.ESTUDIANTE:
        perfil = Estudiante.objects.filter(usuario=usuario).first()
        if perfil:
            perfil_form = EstudianteForm(request.POST or None, instance=perfil)
    elif usuario.rol == Usuario.Rol.PROFESOR:
        perfil = Profesor.objects.filter(usuario=usuario).first()
        if perfil:
            perfil_form = ProfesorForm(request.POST or None, instance=perfil)
    elif usuario.rol == Usuario.Rol.ACUDIENTE:
        perfil = Acudiente.objects.filter(usuario=usuario).first()
        if perfil:
            perfil_form = AcudienteForm(request.POST or None, instance=perfil)

    if request.method == 'POST':
        forms_validos = form.is_valid()
        if perfil_form:
            forms_validos = forms_validos and perfil_form.is_valid()

        if forms_validos:
            form.save()
            if perfil_form:
                perfil_form.save()
            messages.success(request, f'Usuario {usuario.username} actualizado correctamente.')
            return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/editar_usuario.html', {
        'form':        form,
        'perfil_form': perfil_form,
        'usuario':     usuario,
        'titulo':      f'Editar: {usuario.get_full_name()}',
    })


# ─────────────────────────────────────────
# REGISTRO PÚBLICO
# ─────────────────────────────────────────

def registro_view(request):
    return render(request, 'usuarios/registro.html')


def registro_estudiante_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    usuario_form = UsuarioForm(request.POST or None)

    if request.method == 'GET':
        usuario_form.fields['rol'].initial  = Usuario.Rol.ESTUDIANTE
        usuario_form.fields['rol'].disabled = True

    form_est = EstudianteForm(request.POST or None)

    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST)
        usuario_form.fields['rol'].required = False
        form_est = EstudianteForm(request.POST)

        if usuario_form.is_valid() and form_est.is_valid():
            usuario           = usuario_form.save(commit=False)
            usuario.rol       = Usuario.Rol.ESTUDIANTE
            usuario.is_active = False
            usuario.save()

            perfil         = form_est.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

            messages.success(
                request,
                'Cuenta creada correctamente. Espera a que el coordinador active tu cuenta.'
            )
            return redirect('usuarios:login')

    return render(request, 'usuarios/registro_estudiante.html', {
        'usuario_form': usuario_form,
        'form_est':     form_est,
    })


def registro_acudiente_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    usuario_form = UsuarioForm(request.POST or None)

    if request.method == 'GET':
        usuario_form.fields['rol'].initial  = Usuario.Rol.ACUDIENTE
        usuario_form.fields['rol'].disabled = True

    form_acu = AcudienteForm(request.POST or None)

    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST)
        usuario_form.fields['rol'].required = False
        form_acu = AcudienteForm(request.POST)

        if usuario_form.is_valid() and form_acu.is_valid():
            usuario           = usuario_form.save(commit=False)
            usuario.rol       = Usuario.Rol.ACUDIENTE
            usuario.is_active = False
            usuario.save()

            perfil         = form_acu.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            form_acu.save_m2m()

            messages.success(
                request,
                'Cuenta creada correctamente. Espera a que el coordinador active tu cuenta.'
            )
            return redirect('usuarios:login')

    return render(request, 'usuarios/registro_acudiente.html', {
        'usuario_form': usuario_form,
        'form_acu':     form_acu,
    })