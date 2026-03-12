# comercial/models.py

from django.db import models


class Producto(models.Model):
    """
    Artículo disponible para cotización.
    Ejemplos: uniformes, útiles, libros.
    """

    class Categoria(models.TextChoices):
        UNIFORME = 'uniforme', 'Uniforme'
        UTILES   = 'utiles',   'Útiles escolares'
        LIBRO    = 'libro',    'Libro'
        OTRO     = 'otro',     'Otro'

    nombre = models.CharField(
        max_length=150,
        verbose_name='Nombre del producto'
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio'
    )
    categoria = models.CharField(
        max_length=20,
        choices=Categoria.choices,
        default=Categoria.OTRO,
        verbose_name='Categoría'
    )
    stock = models.PositiveIntegerField(
        default=0,
        verbose_name='Stock disponible'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='¿Disponible?'
    )

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f'{self.nombre} (${self.precio})'


class Cotizacion(models.Model):
    """
    Cotización generada para un acudiente.
    Puede incluir varios productos.
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        APROBADA  = 'aprobada',  'Aprobada'
        RECHAZADA = 'rechazada', 'Rechazada'

    acudiente = models.ForeignKey(
        'usuarios.Acudiente',
        on_delete=models.CASCADE,
        related_name='cotizaciones',
        verbose_name='Acudiente'
    )
    productos = models.ManyToManyField(
        Producto,
        through='DetalleCotizacion',
        verbose_name='Productos'
    )
    fecha = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name='Estado'
    )
    observaciones = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Total'
    )

    class Meta:
        verbose_name = 'Cotización'
        verbose_name_plural = 'Cotizaciones'

    def __str__(self):
        return f'Cotización #{self.id} - {self.acudiente}'

    def calcular_total(self):
        """Recalcula y guarda el total sumando todos los detalles."""
        total = sum(
            detalle.subtotal()
            for detalle in self.detalles.all()
        )
        self.total = total
        self.save()


class DetalleCotizacion(models.Model):
    """
    Tabla intermedia entre Cotizacion y Producto.
    Permite guardar la cantidad y el precio al momento
    de la cotización (el precio puede cambiar después).
    """
    cotizacion = models.ForeignKey(
        Cotizacion,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Cotización'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name='Producto'
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        verbose_name='Cantidad'
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio unitario al cotizar'
    )

    class Meta:
        verbose_name = 'Detalle de cotización'
        verbose_name_plural = 'Detalles de cotización'

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f'{self.cantidad}x {self.producto.nombre}'