from django import forms

class PedidoClienteForm(forms.Form):
    nombre = forms.CharField(max_length=120, label="Nombre completo")
    email = forms.EmailField(label="Correo")
    telefono = forms.CharField(max_length=30, required=False, label="Teléfono")
    direccion = forms.CharField(widget=forms.Textarea, required=False, label="Dirección")
    
    # ✅ AGREGA ESTOS CAMPOS FALTANTES:
    fecha_evento = forms.DateField(
        required=False, 
        label="Fecha del evento o entrega",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    detalles = forms.CharField(
        required=False, 
        label="Detalles adicionales",
        widget=forms.Textarea(attrs={'rows': 4, 'placeholder': 'Detalles importantes sobre tu pedido...'})
    )
