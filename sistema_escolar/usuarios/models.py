# usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from django.utils import timezone
from datetime import timedelta


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado.
    Extiende AbstractUser para añadir rol y datos adicionales.
    """

    class Rol(models.TextChoices):
        COORDINADOR = 'coordinador', 'Coordinador'
        PROFESOR    = 'profesor',    'Profesor'
        ESTUDIANTE  = 'estudiante',  'Estudiante'
        ACUDIENTE   = 'acudiente',   'Acudiente'

    class Estado(models.TextChoices):
        PENDIENTE        = 'pendiente',        'Pendiente'
        ACTIVO           = 'activo',           'Activo'
        CAMBIO_REQUERIDO = 'cambio_requerido', 'Cambio de contraseña requerido'
        SUSPENDIDO       = 'suspendido',       'Suspendido'

    rol = models.CharField(
        max_length=20,
        choices=Rol.choices,
        default=Rol.ESTUDIANTE,
        verbose_name='Rol'
    )
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado'
    )
    must_change_password = models.BooleanField(
        default=False,
        verbose_name='Debe cambiar contraseña'
    )
    password_temp_expira = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Expiración contraseña temporal'
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

    def save(self, *args, **kwargs):
        if self.first_name:
            self.first_name = self.first_name.strip().title()
        if self.last_name:
            self.last_name = self.last_name.strip().title()
        if self.username:
            self.username = self.username.strip().lower()
        # Superusuario y coordinador siempre activos
        if self.is_superuser or self.rol == self.Rol.COORDINADOR:
            self.estado               = self.Estado.ACTIVO
            self.must_change_password = False
            self.is_active            = True
        super().save(*args, **kwargs)

    def es_coordinador(self):
        return self.rol == self.Rol.COORDINADOR or self.is_superuser

    def es_profesor(self):
        return self.rol == self.Rol.PROFESOR and not self.is_superuser

    def es_estudiante(self):
        return self.rol == self.Rol.ESTUDIANTE and not self.is_superuser

    def es_acudiente(self):
        return self.rol == self.Rol.ACUDIENTE and not self.is_superuser

    def password_temporal_vigente(self):
        """Verifica si la contraseña temporal no ha expirado"""
        if self.password_temp_expira:
            return timezone.now() < self.password_temp_expira
        return True

    @staticmethod
    def generar_username(first_name, last_name):
        """
        Genera un username único basado en nombre y apellido.
        Ejemplo: Juan Pérez 2025 → jperez2025
        """
        base     = (first_name[0] + last_name).lower()
        base     = ''.join(c for c in base if c.isalnum())
        año      = timezone.now().year
        username = f'{base}{año}'
        contador = 1
        while Usuario.objects.filter(username=username).exists():
            username = f'{base}{año}_{contador}'
            contador += 1
        return username

    @staticmethod
    def generar_password_temporal():
        """
        Genera una contraseña temporal segura de 10 caracteres.
        Incluye mayúsculas, minúsculas, números y símbolos.
        """
        mayusculas = random.choices(string.ascii_uppercase, k=2)
        minusculas = random.choices(string.ascii_lowercase, k=4)
        numeros    = random.choices(string.digits, k=2)
        simbolos   = random.choices('!@#$%', k=2)
        todos      = mayusculas + minusculas + numeros + simbolos
        random.shuffle(todos)
        return ''.join(todos)


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

    def save(self, *args, **kwargs):
        if self.codigo_estudiantil:
            self.codigo_estudiantil = self.codigo_estudiantil.strip().upper()
        super().save(*args, **kwargs)


class Profesor(models.Model):
    """
    Perfil extendido del usuario con rol Profesor.
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

    def save(self, *args, **kwargs):
        if self.especialidad:
            self.especialidad = self.especialidad.strip().capitalize()
        super().save(*args, **kwargs)


class Acudiente(models.Model):
    """
    Perfil extendido del usuario con rol Acudiente.
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

    def save(self, *args, **kwargs):
        if self.parentesco:
            self.parentesco = self.parentesco.strip().capitalize()
        super().save(*args, **kwargs)


class CodigoActivacion(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='codigo_activacion',
        verbose_name='Usuario'
    )
    codigo = models.CharField(
        max_length=6,
        verbose_name='Código'
    )
    creado = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Creado'
    )

    class Meta:
        verbose_name = 'Código de activación'
        verbose_name_plural = 'Códigos de activación'

    def __str__(self):
        return f'{self.usuario.username} — {self.codigo}'

    def esta_vigente(self):
        return timezone.now() < self.creado + timedelta(hours=24)

    @classmethod
    def generar(cls, usuario):
        codigo = ''.join(random.choices(string.digits, k=6))
        obj, _ = cls.objects.update_or_create(
            usuario=usuario,
            defaults={'codigo': codigo}
        )
        return obj