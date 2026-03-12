# comercial/urls.py

from django.urls import path
from . import views

app_name = 'comercial'

urlpatterns = [
    # Productos
    path('productos/',                    views.lista_productos,   name='lista_productos'),
    path('productos/nuevo/',              views.crear_producto,    name='crear_producto'),
    path('productos/<int:pk>/editar/',    views.editar_producto,   name='editar_producto'),
    path('productos/<int:pk>/eliminar/',  views.eliminar_producto, name='eliminar_producto'),

    # Cotizaciones
    path('cotizaciones/',                           views.lista_cotizaciones,  name='lista_cotizaciones'),
    path('cotizaciones/nueva/',                     views.crear_cotizacion,    name='crear_cotizacion'),
    path('cotizaciones/<int:pk>/',                  views.detalle_cotizacion,  name='detalle_cotizacion'),
    path('cotizaciones/<int:pk>/editar/',           views.editar_cotizacion,   name='editar_cotizacion'),
    path('cotizaciones/<int:pk>/eliminar/',         views.eliminar_cotizacion, name='eliminar_cotizacion'),
    path('cotizaciones/<int:pk>/detalle/',          views.agregar_detalle,     name='agregar_detalle'),
    path('cotizaciones/detalle/<int:pk>/eliminar/', views.eliminar_detalle,    name='eliminar_detalle'),
]