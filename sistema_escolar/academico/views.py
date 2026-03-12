# academico/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Curso, Materia, Asignacion, Nota, Asistencia, Actividad, EntregaActividad
from .forms  import (
    CursoForm, MateriaForm, AsignacionForm,
    NotaForm, AsistenciaForm, ActividadForm,
    EntregaActividadForm, CalificarEntregaForm
)
from .decorators import (
    solo_coordinador, coordinador_o_profesor,
    solo_estudiante, no_estudiante
)


# ─────────────────────────────────────────
# CURSOS
# ─────────────────────────────────────────

@login_required
def lista_cursos(request):
    from django.db import models as db_models

    cursos = Curso.objects.all().order_by('año_escolar', 'nombre')

    busqueda    = request.GET.get('q', '')
    año_escolar = request.GET.get('año_escolar', '')
    nivel       = request.GET.get('nivel', '')

    if busqueda:
        cursos = cursos.filter(
            db_models.Q(nombre__icontains=busqueda) 
        )
    if año_escolar:
        cursos = cursos.filter(año_escolar=año_escolar)
    if nivel:
        cursos = cursos.filter(nivel=nivel)

    años_disponibles = Curso.objects.values_list(
        'año_escolar', flat=True
    ).distinct().order_by('-año_escolar')

    # Convertir a int para comparar correctamente en el template
    año_escolar_int = int(año_escolar) if año_escolar else None

    return render(request, 'academico/lista_cursos.html', {
        'cursos':            cursos,
        'busqueda':          busqueda,
        'año_escolar':       año_escolar,
        'año_escolar_int':   año_escolar_int,
        'nivel':             nivel,
        'años_disponibles':  años_disponibles,
        'niveles':           Curso.nivel.field.choices if hasattr(Curso.nivel, 'field') else [],
    })


@login_required
def detalle_curso(request, pk):
    curso        = get_object_or_404(Curso, pk=pk)
    estudiantes  = curso.estudiantes.select_related('usuario').all()
    asignaciones = curso.asignaciones.select_related('materia', 'profesor__usuario').all()
    return render(request, 'academico/detalle_curso.html', {
        'curso':        curso,
        'estudiantes':  estudiantes,
        'asignaciones': asignaciones,
    })


@login_required
@solo_coordinador
def crear_curso(request):
    form = CursoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Curso creado correctamente.')
        return redirect('academico:lista_cursos')
    return render(request, 'academico/form_curso.html', {
        'form':   form,
        'titulo': 'Nuevo curso',
    })


@login_required
@solo_coordinador
def editar_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    form  = CursoForm(request.POST or None, instance=curso)
    if form.is_valid():
        form.save()
        messages.success(request, 'Curso actualizado correctamente.')
        return redirect('academico:lista_cursos')
    return render(request, 'academico/form_curso.html', {
        'form':   form,
        'titulo': f'Editar curso: {curso.nombre}',
    })


@login_required
@solo_coordinador
def eliminar_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    if request.method == 'POST':
        curso.delete()
        messages.success(request, 'Curso eliminado.')
        return redirect('academico:lista_cursos')
    return render(request, 'academico/confirmar_eliminar.html', {
        'objeto': curso,
        'titulo': 'Eliminar curso',
        'volver': 'academico:lista_cursos',
    })


# ─────────────────────────────────────────
# MATERIAS
# ─────────────────────────────────────────

@login_required
def lista_materias(request):
    from django.db import models as db_models

    materias = Materia.objects.all().order_by('nombre')

    busqueda = request.GET.get('q', '')

    if busqueda:
        materias = materias.filter(
            db_models.Q(nombre__icontains=busqueda) |
            db_models.Q(descripcion__icontains=busqueda)
        )

    return render(request, 'academico/lista_materias.html', {
        'materias': materias,
        'busqueda': busqueda,
    })


@login_required
@solo_coordinador
def crear_materia(request):
    form = MateriaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Materia creada correctamente.')
        return redirect('academico:lista_materias')
    return render(request, 'academico/form_materia.html', {
        'form':   form,
        'titulo': 'Nueva materia',
    })


@login_required
@solo_coordinador
def editar_materia(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    form    = MateriaForm(request.POST or None, instance=materia)
    if form.is_valid():
        form.save()
        messages.success(request, 'Materia actualizada.')
        return redirect('academico:lista_materias')
    return render(request, 'academico/form_materia.html', {
        'form':   form,
        'titulo': f'Editar materia: {materia.nombre}',
    })


@login_required
@solo_coordinador
def eliminar_materia(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == 'POST':
        materia.delete()
        messages.success(request, 'Materia eliminada.')
        return redirect('academico:lista_materias')
    return render(request, 'academico/confirmar_eliminar.html', {
        'objeto': materia,
        'titulo': 'Eliminar materia',
        'volver': 'academico:lista_materias',
    })


# ─────────────────────────────────────────
# ASIGNACIONES
# ─────────────────────────────────────────

@login_required
def lista_asignaciones(request):
    user = request.user
    if user.es_profesor():
        from usuarios.models import Profesor
        profesor     = get_object_or_404(Profesor, usuario=user)
        asignaciones = Asignacion.objects.filter(
            profesor=profesor
        ).select_related('curso', 'materia', 'profesor__usuario')
    else:
        asignaciones = Asignacion.objects.all().select_related(
            'curso', 'materia', 'profesor__usuario'
        )
    return render(request, 'academico/lista_asignaciones.html', {
        'asignaciones': asignaciones
    })


@login_required
@solo_coordinador
def crear_asignacion(request):
    form = AsignacionForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Asignación creada correctamente.')
        return redirect('academico:lista_asignaciones')
    return render(request, 'academico/form_asignacion.html', {
        'form':   form,
        'titulo': 'Nueva asignación',
    })


@login_required
@solo_coordinador
def editar_asignacion(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    form       = AsignacionForm(request.POST or None, instance=asignacion)
    if form.is_valid():
        form.save()
        messages.success(request, 'Asignación actualizada.')
        return redirect('academico:lista_asignaciones')
    return render(request, 'academico/form_asignacion.html', {
        'form':   form,
        'titulo': 'Editar asignación',
    })


@login_required
@solo_coordinador
def eliminar_asignacion(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    if request.method == 'POST':
        asignacion.delete()
        messages.success(request, 'Asignación eliminada.')
        return redirect('academico:lista_asignaciones')
    return render(request, 'academico/confirmar_eliminar.html', {
        'objeto': asignacion,
        'titulo': 'Eliminar asignación',
        'volver': 'academico:lista_asignaciones',
    })


# ─────────────────────────────────────────
# NOTAS
# ─────────────────────────────────────────

@login_required
def lista_notas(request):
    user = request.user
    if user.es_estudiante():
        from usuarios.models import Estudiante
        estudiante = get_object_or_404(Estudiante, usuario=user)
        notas = Nota.objects.filter(
            estudiante=estudiante
        ).select_related('asignacion__materia', 'asignacion__curso')
    elif user.es_profesor():
        from usuarios.models import Profesor
        profesor = get_object_or_404(Profesor, usuario=user)
        notas = Nota.objects.filter(
            asignacion__profesor=profesor
        ).select_related('asignacion__materia', 'estudiante__usuario')
    else:
        notas = Nota.objects.all().select_related(
            'asignacion__materia', 'asignacion__curso',
            'estudiante__usuario'
        )
    return render(request, 'academico/lista_notas.html', {'notas': notas})


@login_required
@coordinador_o_profesor
def crear_nota(request):
    form = NotaForm(request.POST or None)
    if request.user.es_profesor():
        from usuarios.models import Profesor
        profesor = get_object_or_404(Profesor, usuario=request.user)
        form.fields['asignacion'].queryset = Asignacion.objects.filter(
            profesor=profesor
        )
    if form.is_valid():
        form.save()
        messages.success(request, 'Nota registrada correctamente.')
        return redirect('academico:lista_notas')
    return render(request, 'academico/form_nota.html', {
        'form':   form,
        'titulo': 'Registrar nota',
    })


@login_required
@coordinador_o_profesor
def editar_nota(request, pk):
    nota = get_object_or_404(Nota, pk=pk)
    form = NotaForm(request.POST or None, instance=nota)
    if form.is_valid():
        form.save()
        messages.success(request, 'Nota actualizada.')
        return redirect('academico:lista_notas')
    return render(request, 'academico/form_nota.html', {
        'form':   form,
        'titulo': 'Editar nota',
    })


# ─────────────────────────────────────────
# ASISTENCIAS
# ─────────────────────────────────────────

@login_required
def lista_asistencias(request):
    from usuarios.models import Profesor as ProfesorModel
    user         = request.user
    asignaciones = Asignacion.objects.all()

    if user.es_profesor():
        profesor     = get_object_or_404(ProfesorModel, usuario=user)
        asignaciones = asignaciones.filter(profesor=profesor)

    asistencias = Asistencia.objects.select_related(
        'estudiante__usuario',
        'asignacion__materia',
        'asignacion__curso'
    ).order_by('-fecha')

    if user.es_profesor():
        profesor    = get_object_or_404(ProfesorModel, usuario=user)
        asistencias = asistencias.filter(asignacion__profesor=profesor)

    asignacion_id = request.GET.get('asignacion')
    fecha         = request.GET.get('fecha')

    if asignacion_id:
        asistencias = asistencias.filter(asignacion_id=asignacion_id)
    if fecha:
        asistencias = asistencias.filter(fecha=fecha)

    return render(request, 'academico/lista_asistencias.html', {
        'asistencias':       asistencias,
        'asignaciones':      asignaciones,
        'filtro_asignacion': asignacion_id,
        'filtro_fecha':      fecha,
    })


@login_required
@coordinador_o_profesor
def registrar_asistencia(request):
    from usuarios.models import Profesor as ProfesorModel, Estudiante as EstudianteModel
    user         = request.user
    asignaciones = Asignacion.objects.select_related('curso', 'materia')

    if user.es_profesor():
        profesor     = get_object_or_404(ProfesorModel, usuario=user)
        asignaciones = asignaciones.filter(profesor=profesor)

    estudiantes = []
    asignacion  = None
    fecha_hoy   = timezone.now().date()

    if request.method == 'GET' and request.GET.get('asignacion'):
        asignacion_id = request.GET.get('asignacion')
        asignacion    = get_object_or_404(Asignacion, pk=asignacion_id)
        estudiantes   = EstudianteModel.objects.filter(
            curso=asignacion.curso
        ).select_related('usuario')

    if request.method == 'POST':
        asignacion_id = request.POST.get('asignacion_id')
        fecha         = request.POST.get('fecha')
        asignacion    = get_object_or_404(Asignacion, pk=asignacion_id)
        estudiantes   = EstudianteModel.objects.filter(
            curso=asignacion.curso
        ).select_related('usuario')

        registros_creados      = 0
        registros_actualizados = 0

        for estudiante in estudiantes:
            presente    = request.POST.get(f'presente_{estudiante.pk}') == 'on'
            observacion = request.POST.get(f'obs_{estudiante.pk}', '')

            asistencia, creada = Asistencia.objects.update_or_create(
                asignacion=asignacion,
                estudiante=estudiante,
                fecha=fecha,
                defaults={
                    'presente':    presente,
                    'observacion': observacion,
                }
            )
            if creada:
                registros_creados += 1
            else:
                registros_actualizados += 1

        messages.success(
            request,
            f'Asistencia registrada: {registros_creados} nuevos, '
            f'{registros_actualizados} actualizados.'
        )
        return redirect('academico:lista_asistencias')

    return render(request, 'academico/registrar_asistencia.html', {
        'asignaciones': asignaciones,
        'asignacion':   asignacion,
        'estudiantes':  estudiantes,
        'fecha_hoy':    fecha_hoy,
    })


@login_required
@coordinador_o_profesor
def editar_asistencia(request, pk):
    asistencia = get_object_or_404(Asistencia, pk=pk)
    form       = AsistenciaForm(request.POST or None, instance=asistencia)
    if form.is_valid():
        form.save()
        messages.success(request, 'Asistencia actualizada.')
        return redirect('academico:lista_asistencias')
    return render(request, 'academico/form_asistencia.html', {
        'form':   form,
        'titulo': 'Editar asistencia',
    })


@login_required
@coordinador_o_profesor
def reporte_asistencia(request):
    from usuarios.models import Profesor as ProfesorModel
    user         = request.user
    asignaciones = Asignacion.objects.select_related('curso', 'materia')

    if user.es_profesor():
        profesor     = get_object_or_404(ProfesorModel, usuario=user)
        asignaciones = asignaciones.filter(profesor=profesor)

    reporte           = []
    asignacion        = None
    asignacion_pk_sel = request.GET.get('asignacion', '')

    if asignacion_pk_sel:
        asignacion  = get_object_or_404(Asignacion, pk=asignacion_pk_sel)
        estudiantes = asignacion.curso.estudiantes.select_related('usuario')

        for est in estudiantes:
            total     = Asistencia.objects.filter(
                asignacion=asignacion, estudiante=est
            ).count()
            presentes = Asistencia.objects.filter(
                asignacion=asignacion, estudiante=est, presente=True
            ).count()
            ausentes   = total - presentes
            porcentaje = round((presentes / total * 100), 1) if total > 0 else 0

            reporte.append({
                'estudiante': est,
                'total':      total,
                'presentes':  presentes,
                'ausentes':   ausentes,
                'porcentaje': porcentaje,
            })

    return render(request, 'academico/reporte_asistencia.html', {
        'asignaciones':      asignaciones,
        'asignacion':        asignacion,
        'asignacion_pk_sel': asignacion_pk_sel,
        'reporte':           reporte,
    })


# ─────────────────────────────────────────
# ACTIVIDADES
# ─────────────────────────────────────────

@login_required
def lista_actividades(request):
    from usuarios.models import Profesor as ProfesorModel, Estudiante as EstudianteModel
    user = request.user

    if user.es_profesor():
        profesor    = get_object_or_404(ProfesorModel, usuario=user)
        actividades = Actividad.objects.filter(
            asignacion__profesor=profesor
        ).select_related('asignacion__materia', 'asignacion__curso').order_by('-fecha_entrega')

    elif user.es_estudiante():
        estudiante  = get_object_or_404(EstudianteModel, usuario=user)
        actividades = Actividad.objects.filter(
            asignacion__curso=estudiante.curso
        ).select_related('asignacion__materia', 'asignacion__curso').order_by('-fecha_entrega')

    else:
        actividades = Actividad.objects.all().select_related(
            'asignacion__materia', 'asignacion__curso'
        ).order_by('-fecha_entrega')

    return render(request, 'academico/lista_actividades.html', {
        'actividades': actividades
    })


@login_required
def detalle_actividad(request, pk):
    from usuarios.models import Estudiante as EstudianteModel
    actividad  = get_object_or_404(Actividad, pk=pk)
    user       = request.user
    entregas   = None
    mi_entrega = None

    if user.es_profesor() or user.es_coordinador():
        entregas = actividad.entregas.select_related('estudiante__usuario').all()

    elif user.es_estudiante():
        estudiante = get_object_or_404(EstudianteModel, usuario=user)
        mi_entrega = actividad.entregas.filter(estudiante=estudiante).first()

    return render(request, 'academico/detalle_actividad.html', {
        'actividad':  actividad,
        'entregas':   entregas,
        'mi_entrega': mi_entrega,
    })


@login_required
@coordinador_o_profesor
def crear_actividad(request):
    from usuarios.models import Profesor as ProfesorModel
    form = ActividadForm(request.POST or None)

    if request.user.es_profesor():
        profesor = get_object_or_404(ProfesorModel, usuario=request.user)
        form.fields['asignacion'].queryset = Asignacion.objects.filter(
            profesor=profesor
        )

    if form.is_valid():
        form.save()
        messages.success(request, 'Actividad creada correctamente.')
        return redirect('academico:lista_actividades')

    return render(request, 'academico/form_actividad.html', {
        'form':   form,
        'titulo': 'Nueva actividad',
    })


@login_required
@coordinador_o_profesor
def editar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    form      = ActividadForm(request.POST or None, instance=actividad)
    if form.is_valid():
        form.save()
        messages.success(request, 'Actividad actualizada.')
        return redirect('academico:lista_actividades')
    return render(request, 'academico/form_actividad.html', {
        'form':   form,
        'titulo': f'Editar: {actividad.titulo}',
    })


@login_required
@coordinador_o_profesor
def eliminar_actividad(request, pk):
    actividad = get_object_or_404(Actividad, pk=pk)
    if request.method == 'POST':
        actividad.delete()
        messages.success(request, 'Actividad eliminada.')
        return redirect('academico:lista_actividades')
    return render(request, 'academico/confirmar_eliminar.html', {
        'objeto': actividad,
        'titulo': 'Eliminar actividad',
        'volver': 'academico:lista_actividades',
    })


@login_required
@solo_estudiante
def entregar_actividad(request, pk):
    from usuarios.models import Estudiante as EstudianteModel
    actividad  = get_object_or_404(Actividad, pk=pk)
    estudiante = get_object_or_404(EstudianteModel, usuario=request.user)

    entrega_existente = actividad.entregas.filter(estudiante=estudiante).first()
    if entrega_existente:
        messages.warning(request, 'Ya realizaste una entrega para esta actividad.')
        return redirect('academico:detalle_actividad', pk=actividad.pk)

    form = EntregaActividadForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        entrega            = form.save(commit=False)
        entrega.actividad  = actividad
        entrega.estudiante = estudiante
        entrega.save()
        messages.success(request, 'Entrega realizada correctamente.')
        return redirect('academico:detalle_actividad', pk=actividad.pk)

    return render(request, 'academico/form_entrega.html', {
        'form':      form,
        'actividad': actividad,
        'titulo':    f'Entregar: {actividad.titulo}',
    })


@login_required
@coordinador_o_profesor
def calificar_entrega(request, pk):
    entrega = get_object_or_404(EntregaActividad, pk=pk)
    form    = CalificarEntregaForm(request.POST or None, instance=entrega)
    if form.is_valid():
        form.save()
        messages.success(request, f'Entrega de {entrega.estudiante.usuario.get_full_name()} calificada.')
        return redirect('academico:detalle_actividad', pk=entrega.actividad.pk)
    return render(request, 'academico/form_calificar.html', {
        'form':    form,
        'entrega': entrega,
        'titulo':  'Calificar entrega',
    })


# ─────────────────────────────────────────
# REPORTES Y ESTADÍSTICAS
# ─────────────────────────────────────────

@login_required
@coordinador_o_profesor
def reportes_inicio(request):
    from usuarios.models import Estudiante as EstudianteModel, Profesor as ProfesorModel
    from django.db.models import Avg

    total_estudiantes = EstudianteModel.objects.count()
    total_profesores  = ProfesorModel.objects.count()
    total_cursos      = Curso.objects.count()
    total_notas       = Nota.objects.count()
    total_asistencias = Asistencia.objects.count()
    total_actividades = Actividad.objects.count()

    promedio_general = Nota.objects.aggregate(promedio=Avg('valor'))['promedio']
    if promedio_general:
        promedio_general = round(promedio_general, 2)

    cursos_data = []
    for curso in Curso.objects.all():
        promedio = Nota.objects.filter(
            asignacion__curso=curso
        ).aggregate(promedio=Avg('valor'))['promedio']
        cursos_data.append({
            'curso':             curso,
            'promedio':          round(promedio, 2) if promedio else None,
            'total_estudiantes': curso.estudiantes.count(),
        })

    return render(request, 'academico/reportes_inicio.html', {
        'total_estudiantes': total_estudiantes,
        'total_profesores':  total_profesores,
        'total_cursos':      total_cursos,
        'total_notas':       total_notas,
        'total_asistencias': total_asistencias,
        'total_actividades': total_actividades,
        'promedio_general':  promedio_general,
        'cursos_data':       cursos_data,
    })


@login_required
@coordinador_o_profesor
def reporte_notas(request):
    from django.db.models import Avg
    from usuarios.models import Profesor as ProfesorModel, Estudiante as EstudianteModel

    user     = request.user
    cursos   = Curso.objects.all()
    materias = Materia.objects.all()
    periodos = Nota.Periodo.choices

    curso_id   = request.GET.get('curso')
    materia_id = request.GET.get('materia')
    periodo    = request.GET.get('periodo')

    notas = Nota.objects.select_related(
        'estudiante__usuario',
        'asignacion__materia',
        'asignacion__curso'
    )

    if user.es_profesor():
        profesor = get_object_or_404(ProfesorModel, usuario=user)
        notas    = notas.filter(asignacion__profesor=profesor)
        cursos   = Curso.objects.filter(
            asignaciones__profesor=profesor
        ).distinct()
        materias = Materia.objects.filter(
            asignaciones__profesor=profesor
        ).distinct()

    if curso_id:
        notas = notas.filter(asignacion__curso_id=curso_id)
    if materia_id:
        notas = notas.filter(asignacion__materia_id=materia_id)
    if periodo:
        notas = notas.filter(periodo=periodo)

    if curso_id:
        estudiantes = EstudianteModel.objects.filter(
            curso_id=curso_id
        ).select_related('usuario')
    else:
        estudiantes = EstudianteModel.objects.select_related('usuario').all()

    reporte = []
    for est in estudiantes:
        notas_est = notas.filter(estudiante=est)
        if notas_est.exists():
            promedio = notas_est.aggregate(promedio=Avg('valor'))['promedio']
            reporte.append({
                'estudiante':  est,
                'total_notas': notas_est.count(),
                'promedio':    round(promedio, 2) if promedio else 0,
                'aprobadas':   notas_est.filter(valor__gte=3.0).count(),
                'reprobadas':  notas_est.filter(valor__lt=3.0).count(),
            })

    reporte.sort(key=lambda x: x['promedio'], reverse=True)

    return render(request, 'academico/reporte_notas.html', {
        'reporte':        reporte,
        'cursos':         cursos,
        'materias':       materias,
        'periodos':       periodos,
        'filtro_curso':   curso_id,
        'filtro_materia': materia_id,
        'filtro_periodo': periodo,
    })


@login_required
@coordinador_o_profesor
def reporte_estudiante(request, pk):
    from django.db.models import Avg
    from usuarios.models import Estudiante as EstudianteModel

    estudiante   = get_object_or_404(EstudianteModel, pk=pk)
    asignaciones = Asignacion.objects.filter(
        curso=estudiante.curso
    ).select_related('materia', 'profesor__usuario')

    materias_data = []
    for asig in asignaciones:
        notas    = Nota.objects.filter(estudiante=estudiante, asignacion=asig).order_by('periodo')
        promedio = notas.aggregate(promedio=Avg('valor'))['promedio']

        total_clases = Asistencia.objects.filter(
            asignacion=asig, estudiante=estudiante
        ).count()
        presentes = Asistencia.objects.filter(
            asignacion=asig, estudiante=estudiante, presente=True
        ).count()
        pct_asistencia = round(
            (presentes / total_clases * 100), 1
        ) if total_clases > 0 else 0

        materias_data.append({
            'asignacion':     asig,
            'notas':          notas,
            'promedio':       round(promedio, 2) if promedio else None,
            'total_clases':   total_clases,
            'presentes':      presentes,
            'pct_asistencia': pct_asistencia,
        })

    promedio_general = Nota.objects.filter(
        estudiante=estudiante
    ).aggregate(promedio=Avg('valor'))['promedio']

    return render(request, 'academico/reporte_estudiante.html', {
        'estudiante':       estudiante,
        'materias_data':    materias_data,
        'promedio_general': round(promedio_general, 2) if promedio_general else None,
    })


@login_required
@coordinador_o_profesor
def reporte_curso(request, pk):
    from django.db.models import Avg
    from usuarios.models import Estudiante as EstudianteModel

    curso       = get_object_or_404(Curso, pk=pk)
    estudiantes = curso.estudiantes.select_related('usuario').all()

    estudiantes_data = []
    for est in estudiantes:
        promedio = Nota.objects.filter(
            estudiante=est, asignacion__curso=curso
        ).aggregate(promedio=Avg('valor'))['promedio']

        asistencias_total = Asistencia.objects.filter(
            estudiante=est, asignacion__curso=curso
        ).count()
        asistencias_presentes = Asistencia.objects.filter(
            estudiante=est, asignacion__curso=curso, presente=True
        ).count()
        pct_asistencia = round(
            (asistencias_presentes / asistencias_total * 100), 1
        ) if asistencias_total > 0 else 0

        estudiantes_data.append({
            'estudiante':     est,
            'promedio':       round(promedio, 2) if promedio else None,
            'pct_asistencia': pct_asistencia,
        })

    estudiantes_data.sort(
        key=lambda x: x['promedio'] if x['promedio'] else 0,
        reverse=True
    )

    asignaciones  = curso.asignaciones.select_related('materia', 'profesor__usuario')
    materias_data = []
    for asig in asignaciones:
        promedio = Nota.objects.filter(
            asignacion=asig
        ).aggregate(promedio=Avg('valor'))['promedio']
        materias_data.append({
            'asignacion': asig,
            'promedio':   round(promedio, 2) if promedio else None,
        })

    return render(request, 'academico/reporte_curso.html', {
        'curso':            curso,
        'estudiantes_data': estudiantes_data,
        'materias_data':    materias_data,
    })