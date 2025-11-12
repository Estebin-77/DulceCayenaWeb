# servicios/forms.py
import datetime
from django import forms
from .models import SolicitudServicio

class SolicitudServicioForm(forms.ModelForm):
    # Forzamos aquí los textos y validaciones en español
    nombre = forms.CharField(
        required=True,
        label="Nombre",
        error_messages={"required": "El nombre es obligatorio."},
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Tu nombre completo"})
    )
    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        error_messages={
            "required": "El correo es obligatorio.",
            "invalid": "Ingresa un correo válido (ej. nombre@dominio.com)."
        },
        widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "ejemplo@correo.com"})
    )
    telefono = forms.CharField(
        required=True,
        label="Teléfono",
        error_messages={"required": "El teléfono es obligatorio."},
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "809-000-0000"})
    )

    # 👇 Campo de fecha obligatorio
    fecha_evento = forms.DateField(
        required=True,
        label="Fecha del evento",
        error_messages={
            "required": "La fecha del evento es obligatoria.",
            "invalid": "Ingresa una fecha válida con el formato AAAA-MM-DD."
        },
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "form-control",
        })
    )

    detalles = forms.CharField(
        required=False,
        label="Detalles adicionales",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Decoración, sabor, cantidad de personas, lugar, horario, etc."
        })
    )

    class Meta:
        model = SolicitudServicio
        fields = ["nombre", "email", "telefono", "fecha_evento", "detalles"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer mínimo HTML5 (cliente) según la fecha local del servidor
        hoy = datetime.date.today().isoformat()
        self.fields["fecha_evento"].widget.attrs["min"] = hoy

    def clean_fecha_evento(self):
        fecha = self.cleaned_data.get("fecha_evento")
        if not fecha:
            # Ya lo maneja 'required', pero por si acaso
            raise forms.ValidationError("La fecha del evento es obligatoria.")
        if fecha < datetime.date.today():
            raise forms.ValidationError("La fecha no puede ser anterior a hoy.")
        return fecha
