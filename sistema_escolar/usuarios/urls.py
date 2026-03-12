# usuarios/urls.py

from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/',     views.login_view,     name='login'),
    path('logout/',    views.logout_view,    name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Registro público
    path('registro/',                  views.registro_view,             name='registro'),
    path('registro/estudiante/',       views.registro_estudiante_view,  name='registro_estudiante'),
    path('registro/acudiente/',        views.registro_acudiente_view,   name='registro_acudiente'),

    # Gestión de usuarios (coordinador)
    path('nuevo/',                         views.crear_usuario,           name='crear_usuario'),
    path('<int:pk>/ver/',                  views.ver_usuario,             name='ver_usuario'),
    path('<int:pk>/editar/',               views.editar_usuario,          name='editar_usuario'),
    path('<int:pk>/perfil/estudiante/',    views.crear_perfil_estudiante, name='crear_perfil_estudiante'),
    path('<int:pk>/perfil/profesor/',      views.crear_perfil_profesor,   name='crear_perfil_profesor'),
    path('<int:pk>/perfil/acudiente/',     views.crear_perfil_acudiente,  name='crear_perfil_acudiente'),
    path('<int:pk>/toggle/',               views.toggle_usuario,          name='toggle_usuario'),
    path('',                               views.lista_usuarios,          name='lista_usuarios'),
]