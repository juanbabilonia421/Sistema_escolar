# comercial/admin.py

from django.contrib import admin
from .models import Producto, Cotizacion, DetalleCotizacion


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'categoria', 'precio', 'stock', 'activo')
    list_filter   = ('categoria', 'activo')
    search_fields = ('nombre',)


class DetalleCotizacionInline(admin.TabularInline):
    """
    Muestra los productos de una cotización
    directamente dentro del formulario de la cotización.
    """
    model  = DetalleCotizacion
    extra  = 1
    fields = ('producto', 'cantidad', 'precio_unitario')


@admin.register(Cotizacion)
class CotizacionAdmin(admin.ModelAdmin):
    list_display  = ('id', 'acudiente', 'fecha', 'estado', 'total')
    list_filter   = ('estado',)
    search_fields = ('acudiente__usuario__last_name',)
    inlines       = [DetalleCotizacionInline]