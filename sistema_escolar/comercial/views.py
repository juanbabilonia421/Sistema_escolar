# comercial/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Producto, Cotizacion, DetalleCotizacion
from .forms  import ProductoForm, CotizacionAcudienteForm, CotizacionCoordinadorForm, DetalleCotizacionForm
from .decorators import solo_coordinador, coordinador_o_acudiente


# ─────────────────────────────────────────
# PRODUCTOS
# ─────────────────────────────────────────

@login_required
def lista_productos(request):
    productos = Producto.objects.all().order_by('categoria', 'nombre')
    return render(request, 'comercial/lista_productos.html', {
        'productos': productos
    })


@login_required
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
def lista_cotizaciones(request):
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
    return render(request, 'comercial/lista_cotizaciones.html', {
        'cotizaciones': cotizaciones
    })


@login_required
def detalle_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    detalles   = cotizacion.detalles.select_related('producto').all()
    return render(request, 'comercial/detalle_cotizacion.html', {
        'cotizacion': cotizacion,
        'detalles':   detalles,
    })


@login_required
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
        detalle.save()
        cotizacion.calcular_total()
        messages.success(request, 'Producto agregado.')
        return redirect('comercial:agregar_detalle', pk=cotizacion.pk)

    detalles = cotizacion.detalles.select_related('producto').all()
    return render(request, 'comercial/agregar_detalle.html', {
        'cotizacion': cotizacion,
        'form':       form,
        'detalles':   detalles,
    })


@login_required
@coordinador_o_acudiente
def eliminar_detalle(request, pk):
    detalle    = get_object_or_404(DetalleCotizacion, pk=pk)
    cotizacion = detalle.cotizacion
    if request.method == 'POST':
        detalle.delete()
        cotizacion.calcular_total()
        messages.success(request, 'Producto eliminado de la cotización.')
    return redirect('comercial:agregar_detalle', pk=cotizacion.pk)


@login_required
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
@solo_coordinador
def eliminar_cotizacion(request, pk):
    cotizacion = get_object_or_404(Cotizacion, pk=pk)
    if request.method == 'POST':
        cotizacion.delete()
        messages.success(request, 'Cotización eliminada.')
        return redirect('comercial:lista_cotizaciones')
    return render(request, 'comercial/confirmar_eliminar.html', {
        'objeto': cotizacion,
        'titulo': 'Eliminar cotización',
        'volver': 'comercial:lista_cotizaciones',
    })