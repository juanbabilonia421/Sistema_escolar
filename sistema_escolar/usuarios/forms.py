# usuarios/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Estudiante, Profesor, Acudiente


class UsuarioForm(UserCreationForm):
    """Formulario para crear un usuario con rol."""
    class Meta:
        model  = Usuario
        fields = ['username', 'first_name', 'last_name',
                  'email', 'rol', 'telefono', 'fecha_nacimiento',
                  'password1', 'password2']
        widgets = {
            'username':        forms.TextInput(attrs={'class': 'form-control'}),
            'first_name':      forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':       forms.TextInput(attrs={'class': 'form-control'}),
            'email':           forms.EmailInput(attrs={'class': 'form-control'}),
            'rol':             forms.Select(attrs={'class': 'form-select'}),
            'telefono':        forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={
                                    'class': 'form-control', 'type': 'date'
                                }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aplicar clases Bootstrap a los campos de contraseña
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class EstudianteForm(forms.ModelForm):
    """Datos adicionales del perfil estudiante."""
    class Meta:
        model  = Estudiante
        fields = ['curso', 'codigo_estudiantil']
        widgets = {
            'curso':              forms.Select(attrs={'class': 'form-select'}),
            'codigo_estudiantil': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfesorForm(forms.ModelForm):
    """Datos adicionales del perfil profesor."""
    class Meta:
        model  = Profesor
        fields = ['especialidad']
        widgets = {
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AcudienteForm(forms.ModelForm):
    """Datos adicionales del perfil acudiente."""
    class Meta:
        model  = Acudiente
        fields = ['parentesco', 'estudiantes']
        widgets = {
            'parentesco':  forms.TextInput(attrs={'class': 'form-control'}),
            'estudiantes': forms.CheckboxSelectMultiple(),
        }