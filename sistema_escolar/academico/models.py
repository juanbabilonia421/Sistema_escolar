# academico/models.py

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Curso(models.Model):
    """
    Representa un grado escolar con su grupo.
    Ejemplo: '10° A', '11° B'
    """

    class Nivel(models.TextChoices):
        PRIMARIA   = 'primaria',   'Primaria'
        SECUNDARIA = 'secundaria', 'Secundaria'
        MEDIA      = 'media',      'Media'

    nombre = models.CharField(
        max_length=50,
        verbose_name='Nombre del curso'
    )
    nivel = models.CharField(
        max_length=20,
        choices=Nivel.choices,
        verbose_name='Nivel'
    )
    año_escolar = models.PositiveIntegerField(
        verbose_name='Año escolar'
    )

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        # No puede haber dos cursos con el mismo nombre en el mismo año
        unique_together = ['nombre', 'año_escolar']

    def __str__(self):
        return f'{self.nombre} ({self.año_escolar})'


class Materia(models.Model):
    """
    Asignatura académica.
    Una materia no pertenece a un curso específico —
    esa relación se define en Asignacion.
    """
    nombre = models.CharField(
        max_length=100,
        verbose_name='Nombre de la materia'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )

    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return self.nombre


class Asignacion(models.Model):
    """
    TABLA CLAVE DEL SISTEMA.

    Representa que un Profesor dicta una Materia en un Curso
    durante un año escolar específico.

    ¿Por qué no usar ManyToMany simple?
    Porque necesitamos guardar el profesor y el año como datos
    adicionales de esa relación. Con ManyToMany simple no es posible.

    Todo lo que ocurre en clases (notas, asistencias, actividades)
    se asocia a esta Asignacion, no a la materia o curso por separado.
    """
    curso = models.ForeignKey(
        Curso,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        verbose_name='Curso'
    )
    materia = models.ForeignKey(
        Materia,
        on_delete=models.CASCADE,
        related_name='asignaciones',
        verbose_name='Materia'
    )
    profesor = models.ForeignKey(
        'usuarios.Profesor',
        on_delete=models.CASCADE,
        related_name='asignaciones',
        verbose_name='Profesor'
    )
    año_escolar = models.PositiveIntegerField(
        verbose_name='Año escolar'
    )

    class Meta:
        verbose_name = 'Asignación'
        verbose_name_plural = 'Asignaciones'
        # Un profesor puede dictar la misma materia en diferentes cursos,
        # pero no puede haber dos registros idénticos.
        unique_together = ['curso', 'materia', 'profesor', 'año_escolar']

    def __str__(self):
        return f'{self.materia} | {self.curso} | {self.profesor}'


class Nota(models.Model):
    """
    Nota de un estudiante en una asignación específica.
    La asignación ya contiene: curso + materia + profesor + año.
    """

    class Periodo(models.TextChoices):
        P1 = 'P1', 'Primer Periodo'
        P2 = 'P2', 'Segundo Periodo'
        P3 = 'P3', 'Tercer Periodo'
        P4 = 'P4', 'Cuarto Periodo'

    asignacion = models.ForeignKey(
        Asignacion,
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name='Asignación'
    )
    estudiante = models.ForeignKey(
        'usuarios.Estudiante',
        on_delete=models.CASCADE,
        related_name='notas',
        verbose_name='Estudiante'
    )
    periodo = models.CharField(
        max_length=2,
        choices=Periodo.choices,
        verbose_name='Periodo'
    )
    valor = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(1.0),
            MaxValueValidator(5.0)
        ],
        verbose_name='Nota (1.0 - 5.0)'
    )

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        # Un estudiante no puede tener dos notas en la misma
        # asignación y el mismo periodo
        unique_together = ['asignacion', 'estudiante', 'periodo']

    def __str__(self):
        return f'{self.estudiante} | {self.asignacion.materia} | {self.periodo}: {self.valor}'

    def aprobado(self):
        """Retorna True si la nota es mayor o igual a 3.0"""
        return self.valor >= 3.0


class Asistencia(models.Model):
    """
    Registro de asistencia de un estudiante a una clase específica.
    """
    asignacion = models.ForeignKey(
        Asignacion,
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name='Asignación'
    )
    estudiante = models.ForeignKey(
        'usuarios.Estudiante',
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name='Estudiante'
    )
    fecha = models.DateField(
        verbose_name='Fecha'
    )
    presente = models.BooleanField(
        default=True,
        verbose_name='¿Presente?'
    )
    observacion = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Observación'
    )

    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        # Un registro de asistencia por estudiante por clase por día
        unique_together = ['asignacion', 'estudiante', 'fecha']

    def __str__(self):
        estado = 'Presente' if self.presente else 'Ausente'
        return f'{self.estudiante} | {self.fecha} | {estado}'


class Actividad(models.Model):
    """
    Tarea, trabajo o evaluación asignada dentro de una clase.
    """
    asignacion = models.ForeignKey(
        Asignacion,
        on_delete=models.CASCADE,
        related_name='actividades',
        verbose_name='Asignación'
    )
    titulo = models.CharField(
        max_length=150,
        verbose_name='Título'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    fecha_entrega = models.DateField(
        verbose_name='Fecha de entrega'
    )
    puntaje_maximo = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=5.0,
        verbose_name='Puntaje máximo'
    )

    class Meta:
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return f'{self.titulo} | {self.asignacion}'


class EntregaActividad(models.Model):
    """
    Entrega de un estudiante para una actividad.
    Registra el archivo entregado y la nota obtenida.
    """
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='entregas',
        verbose_name='Actividad'
    )
    estudiante = models.ForeignKey(
        'usuarios.Estudiante',
        on_delete=models.CASCADE,
        related_name='entregas',
        verbose_name='Estudiante'
    )
    fecha_entrega = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de entrega'
    )
    archivo = models.FileField(
        upload_to='entregas/',
        blank=True,
        null=True,
        verbose_name='Archivo'
    )
    comentario = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentario del estudiante'
    )
    nota_obtenida = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(1.0),
            MaxValueValidator(5.0)
        ],
        verbose_name='Nota obtenida'
    )

    class Meta:
        verbose_name = 'Entrega de actividad'
        verbose_name_plural = 'Entregas de actividades'
        # Un estudiante solo puede entregar una vez por actividad
        unique_together = ['actividad', 'estudiante']

    def __str__(self):
        return f'{self.estudiante} → {self.actividad.titulo}'