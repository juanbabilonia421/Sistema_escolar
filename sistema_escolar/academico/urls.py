# academico/urls.py

from django.urls import path
from . import views

app_name = 'academico'

urlpatterns = [
    # Cursos
    path('cursos/',                     views.lista_cursos,         name='lista_cursos'),
    path('cursos/nuevo/',               views.crear_curso,          name='crear_curso'),
    path('cursos/<int:pk>/',            views.detalle_curso,        name='detalle_curso'),
    path('cursos/<int:pk>/editar/',     views.editar_curso,         name='editar_curso'),
    path('cursos/<int:pk>/eliminar/',   views.eliminar_curso,       name='eliminar_curso'),

    # Materias
    path('materias/',                   views.lista_materias,       name='lista_materias'),
    path('materias/nueva/',             views.crear_materia,        name='crear_materia'),
    path('materias/<int:pk>/editar/',   views.editar_materia,       name='editar_materia'),
    path('materias/<int:pk>/eliminar/', views.eliminar_materia,     name='eliminar_materia'),

    # Asignaciones
    path('asignaciones/',                    views.lista_asignaciones,   name='lista_asignaciones'),
    path('asignaciones/nueva/',              views.crear_asignacion,     name='crear_asignacion'),
    path('asignaciones/<int:pk>/editar/',    views.editar_asignacion,    name='editar_asignacion'),
    path('asignaciones/<int:pk>/eliminar/',  views.eliminar_asignacion,  name='eliminar_asignacion'),

    # Notas
    path('notas/',                  views.lista_notas,  name='lista_notas'),
    path('notas/nueva/',            views.crear_nota,   name='crear_nota'),
    path('notas/<int:pk>/editar/',  views.editar_nota,  name='editar_nota'),

    # Asistencias
    path('asistencias/',                        views.lista_asistencias,    name='lista_asistencias'),
    path('asistencias/registrar/',              views.registrar_asistencia, name='registrar_asistencia'),
    path('asistencias/<int:pk>/editar/',        views.editar_asistencia,    name='editar_asistencia'),
    path('asistencias/reporte/',                views.reporte_asistencia,   name='reporte_asistencia'),

    # Actividades
    path('actividades/',                        views.lista_actividades,    name='lista_actividades'),
    path('actividades/nueva/',                  views.crear_actividad,      name='crear_actividad'),
    path('actividades/<int:pk>/',               views.detalle_actividad,    name='detalle_actividad'),
    path('actividades/<int:pk>/editar/',        views.editar_actividad,     name='editar_actividad'),
    path('actividades/<int:pk>/eliminar/',      views.eliminar_actividad,   name='eliminar_actividad'),

    # Entregas
    path('actividades/<int:pk>/entregar/',      views.entregar_actividad,   name='entregar_actividad'),
    path('entregas/<int:pk>/calificar/',        views.calificar_entrega,    name='calificar_entrega'),
    
    # Al final de urlpatterns en academico/urls.py

    # Reportes
    path('reportes/',                      views.reportes_inicio,    name='reportes_inicio'),
    path('reportes/notas/',                views.reporte_notas,      name='reporte_notas'),
    path('reportes/estudiante/<int:pk>/',  views.reporte_estudiante, name='reporte_estudiante'),
    path('reportes/curso/<int:pk>/',       views.reporte_curso,      name='reporte_curso'),
]
