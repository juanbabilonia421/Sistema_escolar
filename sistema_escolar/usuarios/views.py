# usuarios/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from django.db.models import Avg
from django.core.mail import send_mail
from django.conf import settings as django_settings
from datetime import timedelta

from .models import Usuario, Estudiante, Profesor, Acudiente
from .forms import UsuarioForm, UsuarioInstitucionalForm, EstudianteForm, ProfesorForm, AcudienteForm, CambiarPasswordForm
from .decorators import solo_coordinador, requiere_password_cambiado


# ─────────────────────────
# AUTENTICACIÓN
# ─────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user     = authenticate(request, username=username, password=password)

        if user is not None:

            # Verificar si la contraseña temporal expiró
            if user.must_change_password and not user.password_temporal_vigente():
                user.estado    = Usuario.Estado.SUSPENDIDO
                user.is_active = False
                user.save()
                messages.error(
                    request,
                    'Tu contraseña temporal expiró. Contacta al coordinador.'
                )
                return render(request, 'usuarios/login.html')

            # Verificar si está suspendido
            if user.estado == Usuario.Estado.SUSPENDIDO:
                messages.error(
                    request,
                    'Tu cuenta está suspendida. Contacta al coordinador.'
                )
                return render(request, 'usuarios/login.html')

            # Verificar si está pendiente
            if user.estado == Usuario.Estado.PENDIENTE:
                messages.error(
                    request,
                    'Tu cuenta está pendiente de activación. Contacta al coordinador.'
                )
                return render(request, 'usuarios/login.html')

            login(request, user)

            # Superusuario y coordinador nunca son bloqueados por estado
            if user.is_superuser or user.es_coordinador():
                return redirect('usuarios:dashboard')

            # Si debe cambiar contraseña redirigir obligatoriamente
            if user.must_change_password:
                messages.warning(
                    request,
                    'Debes cambiar tu contraseña temporal antes de continuar.'
                )
                return redirect('usuarios:cambiar_password')

            return redirect('usuarios:dashboard')

        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'usuarios/login.html')


def logout_view(request):
    logout(request)
    return redirect('usuarios:login')


# ─────────────────────────
# DASHBOARD
# ─────────────────────────

@login_required
@requiere_password_cambiado
def dashboard_view(request):
    from academico.models import Curso, Asignacion, Nota, Asistencia, Actividad
    from comercial.models import Cotizacion

    user    = request.user
    context = {'today': timezone.now()}

    if user.es_coordinador():
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
        profesor = Profesor.objects.filter(usuario=user).first()
        if profesor:
            asignaciones = Asignacion.objects.filter(
                profesor=profesor
            ).select_related('materia', 'curso')

            total_clases      = asignaciones.count()
            total_estudiantes = sum(a.curso.estudiantes.count() for a in asignaciones)
            total_actividades = Actividad.objects.filter(
                asignacion__profesor=profesor
            ).count()
            sin_calificar = Actividad.objects.filter(
                asignacion__profesor=profesor,
                entregas__nota_obtenida__isnull=True
            ).distinct().count()

            asignaciones_data = []
            for a in asignaciones:
                total_est   = a.curso.estudiantes.count()
                total_activ = Actividad.objects.filter(asignacion=a).count()
                total_asist = Asistencia.objects.filter(asignacion=a).count()
                presentes   = Asistencia.objects.filter(asignacion=a, presente=True).count()
                pct_asist   = round((presentes / total_asist * 100)) if total_asist > 0 else 0
                asignaciones_data.append({
                    'asignacion':        a,
                    'total_estudiantes': total_est,
                    'total_actividades': total_activ,
                    'pct_asistencia':    pct_asist,
                })

            context.update({
                'mis_asignaciones':  asignaciones,
                'asignaciones_data': asignaciones_data,
                'total_clases':      total_clases,
                'total_estudiantes': total_estudiantes,
                'total_actividades': total_actividades,
                'sin_calificar':     sin_calificar,
            })
        else:
            context.update({
                'mis_asignaciones':  [],
                'asignaciones_data': [],
                'total_clases':      0,
                'total_estudiantes': 0,
                'total_actividades': 0,
                'sin_calificar':     0,
            })

    elif user.es_estudiante():
        estudiante = Estudiante.objects.filter(usuario=user).first()
        if estudiante:
            notas = Nota.objects.filter(
                estudiante=estudiante
            ).select_related('asignacion__materia').order_by('-id')

            total_materias = Asignacion.objects.filter(
                curso=estudiante.curso
            ).values('materia').distinct().count()

            promedio = notas.aggregate(Avg('valor'))['valor__avg']
            promedio = round(promedio, 1) if promedio else 0

            total_asistencias = Asistencia.objects.filter(estudiante=estudiante).count()
            presentes         = Asistencia.objects.filter(
                estudiante=estudiante, presente=True
            ).count()
            pct_asistencia = round((presentes / total_asistencias * 100)) if total_asistencias > 0 else 0

            actividades_pendientes = Actividad.objects.filter(
                asignacion__curso=estudiante.curso
            ).exclude(
                entregas__estudiante=estudiante
            ).distinct()

            context.update({
                'mis_notas':              notas[:10],
                'total_materias':         total_materias,
                'promedio_general':       promedio,
                'pct_asistencia':         pct_asistencia,
                'actividades_pendientes': actividades_pendientes[:5],
                'total_pendientes':       actividades_pendientes.count(),
            })
        else:
            context.update({
                'mis_notas':              [],
                'total_materias':         0,
                'promedio_general':       0,
                'pct_asistencia':         0,
                'actividades_pendientes': [],
                'total_pendientes':       0,
            })

    elif user.es_acudiente():
        from comercial.models import Cotizacion

        acudiente = Acudiente.objects.filter(usuario=user).first()
        if acudiente:
            estudiantes     = acudiente.estudiantes.select_related('usuario', 'curso').all()
            cotizaciones    = Cotizacion.objects.filter(acudiente=acudiente).order_by('-fecha')
            total_cots      = cotizaciones.count()
            cots_pendientes = cotizaciones.filter(estado='pendiente').count()
            total_valor     = sum(c.total for c in cotizaciones)

            ids_estudiantes = estudiantes.values_list('id', flat=True)

            total_notas = Nota.objects.filter(
                estudiante__in=ids_estudiantes
            ).count()

            promedio_general = Nota.objects.filter(
                estudiante__in=ids_estudiantes
            ).aggregate(Avg('valor'))['valor__avg']
            promedio_general = round(promedio_general, 1) if promedio_general else 0

            total_asistencias = Asistencia.objects.filter(
                estudiante__in=ids_estudiantes
            ).count()
            presentes = Asistencia.objects.filter(
                estudiante__in=ids_estudiantes, presente=True
            ).count()
            pct_asistencia = round((presentes / total_asistencias * 100)) if total_asistencias > 0 else 0

            actividades_pendientes = Actividad.objects.filter(
                asignacion__curso__estudiantes__in=ids_estudiantes
            ).exclude(
                entregas__estudiante__in=ids_estudiantes
            ).distinct().count()

            context.update({
                'mis_estudiantes':        estudiantes,
                'total_hijos':            estudiantes.count(),
                'mis_cotizaciones':       cotizaciones[:5],
                'total_cotizaciones':     total_cots,
                'cots_pendientes':        cots_pendientes,
                'total_valor':            total_valor,
                'total_notas':            total_notas,
                'promedio_general':       promedio_general,
                'total_asistencias':      total_asistencias,
                'pct_asistencia':         pct_asistencia,
                'actividades_pendientes': actividades_pendientes,
            })
        else:
            context.update({
                'mis_estudiantes':        [],
                'total_hijos':            0,
                'mis_cotizaciones':       [],
                'total_cotizaciones':     0,
                'cots_pendientes':        0,
                'total_valor':            0,
                'total_notas':            0,
                'promedio_general':       0,
                'total_asistencias':      0,
                'pct_asistencia':         0,
                'actividades_pendientes': 0,
            })

    return render(request, 'usuarios/dashboard.html', context)


# ─────────────────────────
# CAMBIAR CONTRASEÑA
# ─────────────────────────

@login_required
def cambiar_password_view(request):
    if not request.user.must_change_password:
        return redirect('usuarios:dashboard')

    form = CambiarPasswordForm(request.POST or None)

    if form.is_valid():
        nueva_password = form.cleaned_data['password1']
        user           = request.user

        user.set_password(nueva_password)
        user.must_change_password = False
        user.estado               = Usuario.Estado.ACTIVO
        user.password_temp_expira = None
        user.is_active            = True
        user.save()

        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, user)

        messages.success(
            request,
            '¡Contraseña actualizada correctamente! Bienvenido al sistema.'
        )
        return redirect('usuarios:dashboard')

    return render(request, 'usuarios/cambiar_password.html', {
        'form': form,
    })


# ─────────────────────────
# REGISTROS PÚBLICOS
# ─────────────────────────

def registro_view(request):
    return render(request, 'usuarios/registro.html')


def registro_estudiante_view(request):
    if request.user.is_authenticated:
        return redirect('usuarios:dashboard')

    usuario_form = UsuarioForm(request.POST or None)
    form_est     = EstudianteForm(request.POST or None)

    if request.method == 'GET':
        usuario_form.fields['rol'].initial  = Usuario.Rol.ESTUDIANTE
        usuario_form.fields['rol'].disabled = True

    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST)
        usuario_form.fields['rol'].required = False
        form_est = EstudianteForm(request.POST)

        if usuario_form.is_valid() and form_est.is_valid():
            usuario           = usuario_form.save(commit=False)
            usuario.rol       = Usuario.Rol.ESTUDIANTE
            usuario.is_active = False
            usuario.estado    = Usuario.Estado.PENDIENTE
            usuario.save()

            perfil         = form_est.save(commit=False)
            perfil.usuario = usuario
            perfil.save()

            messages.success(
                request,
                'Cuenta creada. Espera a que el coordinador la active.'
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
    form_acu     = AcudienteForm(request.POST or None)

    if request.method == 'GET':
        usuario_form.fields['rol'].initial  = Usuario.Rol.ACUDIENTE
        usuario_form.fields['rol'].disabled = True

    if request.method == 'POST':
        usuario_form = UsuarioForm(request.POST)
        usuario_form.fields['rol'].required = False
        form_acu = AcudienteForm(request.POST)

        if usuario_form.is_valid() and form_acu.is_valid():
            usuario           = usuario_form.save(commit=False)
            usuario.rol       = Usuario.Rol.ACUDIENTE
            usuario.is_active = False
            usuario.estado    = Usuario.Estado.PENDIENTE
            usuario.save()

            perfil         = form_acu.save(commit=False)
            perfil.usuario = usuario
            perfil.save()
            form_acu.save_m2m()

            messages.success(
                request,
                'Cuenta creada correctamente. Espera a que el coordinador la active.'
            )
            return redirect('usuarios:login')

    return render(request, 'usuarios/registro_acudiente.html', {
        'usuario_form': usuario_form,
        'form_acu':     form_acu,
    })


# ─────────────────────────
# VERIFICACIÓN CÓDIGO
# ─────────────────────────

def verificar_codigo_view(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.is_active:
        messages.info(request, 'Tu cuenta ya está activa.')
        return redirect('usuarios:login')

    if request.method == 'POST':
        from .models import CodigoActivacion
        codigo_ingresado = request.POST.get('codigo', '').strip()

        try:
            codigo_obj = CodigoActivacion.objects.get(usuario=usuario)

            if not codigo_obj.esta_vigente():
                messages.error(request, 'El código expiró. Contacta al coordinador.')
                return redirect('usuarios:login')

            if codigo_ingresado == codigo_obj.codigo:
                usuario.is_active = True
                usuario.save()
                codigo_obj.delete()
                messages.success(request, '¡Cuenta activada! Ya puedes iniciar sesión.')
                return redirect('usuarios:login')
            else:
                messages.error(request, 'Código incorrecto. Intenta de nuevo.')

        except CodigoActivacion.DoesNotExist:
            messages.error(request, 'No hay código activo. Contacta al coordinador.')
            return redirect('usuarios:login')

    return render(request, 'usuarios/verificar_codigo.html', {
        'usuario': usuario,
    })


# ─────────────────────────
# CRUD USUARIOS
# ─────────────────────────

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
    if estado:
        usuarios = usuarios.filter(estado=estado)

    return render(request, 'usuarios/lista_usuarios.html', {
        'usuarios': usuarios,
        'busqueda': busqueda,
        'rol':      rol,
        'estado':   estado,
        'roles':    Usuario.Rol.choices,
        'estados':  Usuario.Estado.choices,
    })


@login_required
@solo_coordinador
def crear_usuario(request):
    form = UsuarioInstitucionalForm(request.POST or None)

    if form.is_valid():
        usuario  = form.save(commit=False)
        username = Usuario.generar_username(usuario.first_name, usuario.last_name)
        password = Usuario.generar_password_temporal()

        usuario.username  = username
        usuario.is_active = True

        # Coordinador queda activo directo, los demás deben cambiar contraseña
        if usuario.rol == Usuario.Rol.COORDINADOR:
            usuario.estado               = Usuario.Estado.ACTIVO
            usuario.must_change_password = False
        else:
            usuario.estado               = Usuario.Estado.CAMBIO_REQUERIDO
            usuario.must_change_password = True
            usuario.password_temp_expira = timezone.now() + timedelta(hours=48)

        usuario.set_password(password)
        usuario.save()

        try:
            send_mail(
                subject='Bienvenido al Sistema Escolar — Tus credenciales de acceso',
                message=f'''Hola {usuario.get_full_name()},

Tu cuenta ha sido creada en el Sistema Escolar.

Tus credenciales de acceso son:

  Usuario:     {username}
  Contraseña:  {password}

{"Esta contraseña es temporal y expira en 48 horas. Al iniciar sesión por primera vez deberás cambiarla." if usuario.rol != Usuario.Rol.COORDINADOR else ""}

Accede aquí: http://127.0.0.1:8000/usuarios/login/

Si tienes algún problema contacta al coordinador.

Saludos,
Sistema Escolar''',
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[usuario.email],
                fail_silently=False,
            )
            messages.success(
                request,
                f'Usuario {username} creado. Credenciales enviadas a {usuario.email}.'
            )
        except Exception:
            messages.warning(
                request,
                f'Usuario {username} creado con contraseña: {password} — No se pudo enviar el correo.'
            )

        if usuario.rol == Usuario.Rol.ESTUDIANTE:
            return redirect('usuarios:crear_perfil_estudiante', pk=usuario.pk)
        elif usuario.rol == Usuario.Rol.PROFESOR:
            return redirect('usuarios:crear_perfil_profesor', pk=usuario.pk)
        elif usuario.rol == Usuario.Rol.ACUDIENTE:
            return redirect('usuarios:crear_perfil_acudiente', pk=usuario.pk)
        else:
            return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/form_crear_usuario_institucional.html', {
        'form':   form,
        'titulo': 'Nuevo usuario',
    })


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
        if usuario.is_active:
            usuario.is_active = False
            usuario.estado    = Usuario.Estado.SUSPENDIDO
            usuario.save()
            messages.success(request, f'{usuario.get_full_name()} suspendido.')
        else:
            usuario.is_active = True
            usuario.estado    = Usuario.Estado.ACTIVO
            usuario.save()
            messages.success(request, f'{usuario.get_full_name()} activado.')

    return redirect('usuarios:lista_usuarios')


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
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if usuario.is_superuser:
        messages.error(request, 'No puedes eliminar al superusuario.')
        return redirect('usuarios:lista_usuarios')

    if usuario == request.user:
        messages.error(request, 'No puedes eliminarte a ti mismo.')
        return redirect('usuarios:lista_usuarios')

    if request.method == 'POST':
        nombre = usuario.get_full_name()
        usuario.delete()
        messages.success(request, f'Usuario {nombre} eliminado correctamente.')
        return redirect('usuarios:lista_usuarios')

    return render(request, 'usuarios/confirmar_eliminar_usuario.html', {
        'usuario': usuario,
    })