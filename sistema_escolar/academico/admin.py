# academico/admin.py

from django.contrib import admin
from .models import (
    Curso, Materia, Asignacion,
    Nota, Asistencia, Actividad, EntregaActividad
)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'nivel', 'año_escolar')
    list_filter   = ('nivel', 'año_escolar')
    search_fields = ('nombre',)


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display  = ('nombre',)
    search_fields = ('nombre',)


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display  = ('materia', 'curso', 'profesor', 'año_escolar')
    list_filter   = ('año_escolar', 'curso', 'materia')
    search_fields = ('materia__nombre', 'profesor__usuario__last_name')


@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display  = ('estudiante', 'asignacion', 'periodo', 'valor', 'aprobado')
    list_filter   = ('periodo', 'asignacion__curso', 'asignacion__materia')
    search_fields = ('estudiante__usuario__last_name',)


@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display  = ('estudiante', 'asignacion', 'fecha', 'presente')
    list_filter   = ('presente', 'fecha', 'asignacion__curso')
    search_fields = ('estudiante__usuario__last_name',)


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display  = ('titulo', 'asignacion', 'fecha_entrega', 'puntaje_maximo')
    list_filter   = ('asignacion__curso', 'asignacion__materia')
    search_fields = ('titulo',)


@admin.register(EntregaActividad)
class EntregaActividadAdmin(admin.ModelAdmin):
    list_display  = ('estudiante', 'actividad', 'fecha_entrega', 'nota_obtenida')
    search_fields = ('estudiante__usuario__last_name', 'actividad__titulo')