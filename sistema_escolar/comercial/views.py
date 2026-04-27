# comercial/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Cotizacion, DetalleCotizacion
from .forms  import ProductoForm, CotizacionAcudienteForm, CotizacionCoordinadorForm, DetalleCotizacionForm
from .decorators import solo_coordinador, coordinador_o_acudiente
from usuarios.decorators import requiere_password_cambiado


# ─────────────────────────────────────────
# PRODUCTOS
# ─────────────────────────────────────────

@login_required
@requiere_password_cambiado
def lista_productos(request):
    from django.db import models as db_models

    productos = Producto.objects.all().order_by('categoria', 'nombre')

    busqueda  = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    estado    = request.GET.get('estado', '')

    if busqueda:
        productos = productos.filter(
            db_models.Q(nombre__icontains=busqueda) |
            db_models.Q(descripcion__icontains=busqueda)
        )
    if categoria:
        productos = productos.filter(categoria=categoria)
    if estado == 'activo':
        productos = productos.filter(activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(activo=False)

    categorias = Producto.Categoria.choices

    return render(request, 'comercial/lista_productos.html', {
        'productos':  productos,
        'busqueda':   busqueda,
        'categoria':  categoria,
        'estado':     estado,
        'categorias': categorias,
    })


@login_required
@requiere_password_cambiado
@solo_coordinador
def crear_producto(request):
    form = ProductoForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto creado correctamente.')
        return redirect('comercial:lista_productos')
    return render(request, 'comercial/form_producto.html', {
        'form':   form,
        'titulo': 'Nuevo producto',
    })


@login_required
@requiere_password_cambiado
@solo_coordinador
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form     = ProductoForm(request.POST or None, instance=producto)
    if form.is_valid():
        form.save()
        messages.success(request, 'Producto actualizado.')
        return redirect('comercial:lista_productos')
    return render(request, 'comercial/form_producto.html', {
        'form':   form,
        'titulo': f'Editar: {producto.nombre}',
    })


@login_required
@requiere_password_cambiado
@solo_coordinador
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, 'Producto eliminado.')
        return redirect('comercial:lista_productos')
    return render(request, 'comercial/confirmar_eliminar.html', {
        'objeto': producto,
        'titulo': 'Eliminar producto',
        'volver': 'comercial:lista_productos',
    })


# ─────────────────────────────────────────
# COTIZACIONES
# ─────────────────────────────────────────

@login_required
@requiere_password_cambiado
def lista_cotizaciones(request):
    from django.db import models as db_models
    user = request.user

    if user.es_acudiente():
        from usuarios.models import Acudiente
        acudiente    = get_object_or_404(Acudiente, usuario=user)
        cotizaciones = Cotizacion.objects.filter(
            acudiente=acudiente
        ).order_by('-fecha')
    else:
        cotizaciones = Cotizacion.objects.all().select_related(
            'acudiente__usuario'
        ).order_by('-fecha')

    busqueda = request.GET.get('q', '')
    estado   = request.GET.get('estado', '')

    if busqueda:
        cotizaciones = cotizaciones.filter(
            db_models.Q(acudiente__usuario__first_name__icontains=busqueda) |
            db_models.Q(acudiente__usuario__last_name__icontains=busqueda)  |
            db_models.Q(observaciones__icontains=busqueda)
        )
    if estado:
        cotizaciones = cotizaciones.filter(estado=estado)

    estados = Cotizacion.estado.field.choices if hasattr(Cotizacion.estado, 'field') else []

    return render(request, 'comercial/lista_cotizaciones.html', {
        'cotizaciones': cotizaciones,
        'busqueda':     busqueda,
        'estado':       estado,
        'estados':      estados,
    })


@login_required
@requiere_password_cambiado
def detalle_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    detalles   = cotizacion.detalles.select_related('producto').all()
    return render(request, 'comercial/detalle_cotizacion.html', {
        'cotizacion': cotizacion,
        'detalles':   detalles,
    })


@login_required
@requiere_password_cambiado
@coordinador_o_acudiente
def crear_cotizacion(request):
    user = request.user

    if user.es_acudiente():
        from usuarios.models import Acudiente
        acudiente = get_object_or_404(Acudiente, usuario=user)
        form = CotizacionAcudienteForm(request.POST or None)
    else:
        form = CotizacionCoordinadorForm(request.POST or None)

    if form.is_valid():
        cotizacion = form.save(commit=False)
        if user.es_acudiente():
            from usuarios.models import Acudiente
            cotizacion.acudiente = get_object_or_404(Acudiente, usuario=user)
            cotizacion.estado    = 'pendiente'
        cotizacion.save()
        messages.success(request, 'Cotización creada. Ahora agrega los productos.')
        return redirect('comercial:agregar_detalle', pk=cotizacion.pk)

    return render(request, 'comercial/form_cotizacion.html', {
        'form':   form,
        'titulo': 'Nueva cotización',
    })


@login_required
@requiere_password_cambiado
@coordinador_o_acudiente
def agregar_detalle(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    form       = DetalleCotizacionForm(request.POST or None)

    form.fields['producto'].queryset = Producto.objects.filter(
        activo=True, stock__gt=0
    )

    if form.is_valid():
        detalle            = form.save(commit=False)
        detalle.cotizacion = cotizacion
        producto           = detalle.producto
        cantidad           = detalle.cantidad

        if cantidad > producto.stock:
            messages.error(
                request,
                f'Stock insuficiente. Solo hay {producto.stock} unidades de {producto.nombre}.'
            )
            detalles = cotizacion.detalles.select_related('producto').all()
            return render(request, 'comercial/agregar_detalle.html', {
                'cotizacion': cotizacion,
                'form':       form,
                'detalles':   detalles,
            })

        detalle.precio_unitario = producto.precio
        detalle.save()

        producto.stock -= cantidad
        producto.save()

        cotizacion.calcular_total()
        messages.success(request, f'{producto.nombre} agregado a la cotización.')
        return redirect('comercial:agregar_detalle', pk=cotizacion.pk)

    detalles = cotizacion.detalles.select_related('producto').all()
    return render(request, 'comercial/agregar_detalle.html', {
        'cotizacion': cotizacion,
        'form':       form,
        'detalles':   detalles,
    })


@login_required
@requiere_password_cambiado
@coordinador_o_acudiente
def eliminar_detalle(request, pk):
    detalle    = get_object_or_404(DetalleCotizacion, pk=pk)
    cotizacion = detalle.cotizacion

    if request.method == 'POST':
        producto        = detalle.producto
        producto.stock += detalle.cantidad
        producto.save()

        detalle.delete()
        cotizacion.calcular_total()
        messages.success(request, 'Producto eliminado de la cotización.')

    return redirect('comercial:agregar_detalle', pk=cotizacion.pk)


@login_required
@requiere_password_cambiado
@solo_coordinador
def editar_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    form       = CotizacionCoordinadorForm(request.POST or None, instance=cotizacion)
    if form.is_valid():
        form.save()
        messages.success(request, 'Cotización actualizada.')
        return redirect('comercial:detalle_cotizacion', pk=cotizacion.pk)
    return render(request, 'comercial/form_cotizacion.html', {
        'form':   form,
        'titulo': f'Editar cotización #{cotizacion.pk}',
    })


@login_required
@requiere_password_cambiado
@solo_coordinador
def eliminar_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    if request.method == 'POST':
        for detalle in cotizacion.detalles.all():
            producto        = detalle.producto
            producto.stock += detalle.cantidad
            producto.save()

        cotizacion.delete()
        messages.success(request, 'Cotización eliminada.')
        return redirect('comercial:lista_cotizaciones')

    return render(request, 'comercial/confirmar_eliminar.html', {
        'objeto': cotizacion,
        'titulo': 'Eliminar cotización',
        'volver': 'comercial:lista_cotizaciones',
    })