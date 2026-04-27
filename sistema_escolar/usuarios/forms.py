# usuarios/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Estudiante, Profesor, Acudiente


class UsuarioForm(UserCreationForm):
    """Formulario para crear un usuario con rol (registro público o manual con contraseña)."""
    class Meta:
        model  = Usuario
        fields = ['username', 'first_name', 'last_name',
                  'email', 'rol', 'telefono', 'fecha_nacimiento',
                  'password1', 'password2']
        widgets = {
            'username':         forms.TextInput(attrs={'class': 'form-control'}),
            'first_name':       forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':        forms.TextInput(attrs={'class': 'form-control'}),
            'email':            forms.EmailInput(attrs={'class': 'form-control'}),
            'rol':              forms.Select(attrs={'class': 'form-select'}),
            'telefono':         forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={
                                    'class': 'form-control', 'type': 'date'
                                }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'


class UsuarioInstitucionalForm(forms.ModelForm):
    """
    Formulario institucional para que el coordinador cree cuentas.
    NO pide username ni contraseña — el sistema los genera automáticamente.
    """
    class Meta:
        model  = Usuario
        fields = ['first_name', 'last_name', 'email', 'rol',
                  'telefono', 'fecha_nacimiento']
        widgets = {
            'first_name':       forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Nombre'
                                }),
            'last_name':        forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Apellido'
                                }),
            'email':            forms.EmailInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'correo@ejemplo.com'
                                }),
            'rol':              forms.Select(attrs={'class': 'form-select'}),
            'telefono':         forms.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Opcional'
                                }),
            'fecha_nacimiento': forms.DateInput(attrs={
                                    'class': 'form-control', 'type': 'date'
                                }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required      = True
        self.fields['last_name'].required       = True
        self.fields['email'].required           = True
        self.fields['telefono'].required        = False
        self.fields['fecha_nacimiento'].required = False

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email


class EstudianteForm(forms.ModelForm):
    class Meta:
        model  = Estudiante
        fields = ['curso', 'codigo_estudiantil']
        widgets = {
            'curso':              forms.Select(attrs={'class': 'form-select'}),
            'codigo_estudiantil': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ProfesorForm(forms.ModelForm):
    class Meta:
        model  = Profesor
        fields = ['especialidad']
        widgets = {
            'especialidad': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AcudienteForm(forms.ModelForm):
    class Meta:
        model  = Acudiente
        fields = ['parentesco', 'estudiantes']
        widgets = {
            'parentesco':  forms.TextInput(attrs={'class': 'form-control'}),
            'estudiantes': forms.CheckboxSelectMultiple(),
        }


class CambiarPasswordForm(forms.Form):
    """Formulario para que el usuario cambie su contraseña temporal."""
    password1 = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña',
            'id': 'id_password1'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite la contraseña',
            'id': 'id_password2'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')

        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError('Las contraseñas no coinciden.')
            if len(p1) < 8:
                raise forms.ValidationError('La contraseña debe tener al menos 8 caracteres.')
            if not any(c.isupper() for c in p1):
                raise forms.ValidationError('Debe contener al menos una mayúscula.')
            if not any(c.isdigit() for c in p1):
                raise forms.ValidationError('Debe contener al menos un número.')
            if not any(c in '!@#$%^&*' for c in p1):
                raise forms.ValidationError('Debe contener al menos un símbolo (!@#$%^&*).')

        return cleaned_data