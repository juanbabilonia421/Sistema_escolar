# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Estudiante, Profesor, Acudiente


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Extiende el admin por defecto de Django para mostrar
    los campos personalizados (rol, teléfono, fecha_nacimiento).
    """
    list_display  = ('username', 'get_full_name', 'email', 'rol', 'is_active')
    list_filter   = ('rol', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering      = ('last_name', 'first_name')

    # Añadir los campos personalizados al formulario del admin
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono', 'fecha_nacimiento')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono', 'fecha_nacimiento')
        }),
    )


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'codigo_estudiantil', 'curso', 'fecha_ingreso')
    list_filter   = ('curso',)
    search_fields = ('usuario__first_name', 'usuario__last_name', 'codigo_estudiantil')


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'especialidad')
    search_fields = ('usuario__first_name', 'usuario__last_name')


@admin.register(Acudiente)
class AcudienteAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'parentesco')
    search_fields = ('usuario__first_name', 'usuario__last_name')
    filter_horizontal = ('estudiantes',)  # Widget más cómodo para ManyToMany