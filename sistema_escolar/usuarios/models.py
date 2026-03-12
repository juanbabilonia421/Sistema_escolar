# usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado.
    Extiende AbstractUser para añadir rol y datos adicionales.
    El superusuario creado con createsuperuser será el Coordinador.
    """

    class Rol(models.TextChoices):
        COORDINADOR = 'coordinador', 'Coordinador'
        PROFESOR    = 'profesor',    'Profesor'
        ESTUDIANTE  = 'estudiante',  'Estudiante'
        ACUDIENTE   = 'acudiente',   'Acudiente'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
        verbose_name='Rol'
    )
    telefono = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de nacimiento'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.get_full_name()} ({self.get_rol_display()})'

    # Métodos de conveniencia para verificar roles en templates y vistas
    def es_coordinador(self):
    # El superusuario siempre es coordinador
        return self.rol == self.Rol.COORDINADOR or self.is_superuser

    def es_profesor(self):
        return self.rol == self.Rol.PROFESOR and not self.is_superuser

    def es_estudiante(self):
        return self.rol == self.Rol.ESTUDIANTE and not self.is_superuser

    def es_acudiente(self):
        return self.rol == self.Rol.ACUDIENTE and not self.is_superuser


class Estudiante(models.Model):
    """
    Perfil extendido del usuario con rol Estudiante.
    Cada estudiante pertenece a un curso.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_estudiante',
        verbose_name='Usuario'
    )
    curso = models.ForeignKey(
        'academico.Curso',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='estudiantes',
        verbose_name='Curso'
    )
    codigo_estudiantil = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Código estudiantil'
    )
    fecha_ingreso = models.DateField(
        auto_now_add=True,
        verbose_name='Fecha de ingreso'
    )

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return f'{self.usuario.get_full_name()} - {self.curso}'


class Profesor(models.Model):
    """
    Perfil extendido del usuario con rol Profesor.
    Los profesores NO pertenecen a un curso específico.
    Su relación con cursos y materias se maneja mediante Asignacion.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_profesor',
        verbose_name='Usuario'
    )
    especialidad = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Especialidad'
    )

    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'

    def __str__(self):
        return f'Prof. {self.usuario.get_full_name()}'


class Acudiente(models.Model):
    """
    Perfil extendido del usuario con rol Acudiente.
    Un acudiente puede tener varios estudiantes a cargo.
    """
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_acudiente',
        verbose_name='Usuario'
    )
    estudiantes = models.ManyToManyField(
        Estudiante,
        blank=True,
        related_name='acudientes',
        verbose_name='Estudiantes a cargo'
    )
    parentesco = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Parentesco'
    )

    class Meta:
        verbose_name = 'Acudiente'
        verbose_name_plural = 'Acudientes'

    def __str__(self):
        return f'{self.usuario.get_full_name()} (Acudiente)'