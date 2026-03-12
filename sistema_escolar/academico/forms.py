# academico/forms.py

from django import forms
from .models import Curso, Materia, Asignacion, Nota, Asistencia, Actividad, EntregaActividad


class CursoForm(forms.ModelForm):
    class Meta:
        model  = Curso
        fields = ['nombre', 'nivel', 'año_escolar']
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'form-control'}),
            'nivel':       forms.Select(attrs={'class': 'form-select'}),
            'año_escolar': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class MateriaForm(forms.ModelForm):
    class Meta:
        model  = Materia
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre':      forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class AsignacionForm(forms.ModelForm):
    class Meta:
        model  = Asignacion
        fields = ['curso', 'materia', 'profesor', 'año_escolar']
        widgets = {
            'curso':       forms.Select(attrs={'class': 'form-select'}),
            'materia':     forms.Select(attrs={'class': 'form-select'}),
            'profesor':    forms.Select(attrs={'class': 'form-select'}),
            'año_escolar': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class NotaForm(forms.ModelForm):
    class Meta:
        model  = Nota
        fields = ['asignacion', 'estudiante', 'periodo', 'valor']
        widgets = {
            'asignacion': forms.Select(attrs={'class': 'form-select'}),
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'periodo':    forms.Select(attrs={'class': 'form-select'}),
            'valor':      forms.NumberInput(attrs={
                            'class': 'form-control',
                            'step': '0.1', 'min': '1.0', 'max': '5.0'
                          }),
        }


class AsistenciaForm(forms.ModelForm):
    class Meta:
        model  = Asistencia
        fields = ['asignacion', 'estudiante', 'fecha', 'presente', 'observacion']
        widgets = {
            'asignacion':  forms.Select(attrs={'class': 'form-select'}),
            'estudiante':  forms.Select(attrs={'class': 'form-select'}),
            'fecha':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'presente':    forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'observacion': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ActividadForm(forms.ModelForm):
    class Meta:
        model  = Actividad
        fields = ['asignacion', 'titulo', 'descripcion', 'fecha_entrega', 'puntaje_maximo']
        widgets = {
            'asignacion':     forms.Select(attrs={'class': 'form-select'}),
            'titulo':         forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion':    forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'fecha_entrega':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'puntaje_maximo': forms.NumberInput(attrs={
                                'class': 'form-control',
                                'step': '0.1', 'min': '1.0', 'max': '5.0'
                            }),
        }


class EntregaActividadForm(forms.ModelForm):
    """Formulario para que el estudiante entregue una actividad."""
    class Meta:
        model  = EntregaActividad
        fields = ['archivo', 'comentario']
        widgets = {
            'archivo':    forms.FileInput(attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={
                            'class': 'form-control', 'rows': 3,
                            'placeholder': 'Comentario opcional...'
                        }),
        }


class CalificarEntregaForm(forms.ModelForm):
    """Formulario para que el profesor califique una entrega."""
    class Meta:
        model  = EntregaActividad
        fields = ['nota_obtenida']
        widgets = {
            'nota_obtenida': forms.NumberInput(attrs={
                            'class': 'form-control',
                            'step': '0.1', 'min': '1.0', 'max': '5.0'
                        }),
        }