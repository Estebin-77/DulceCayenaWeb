from django.db import models
from django.utils.text import slugify

class Servicio(models.Model):
    titulo = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, max_length=160)
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='servicios', blank=True, null=True)
    precio_desde = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        super().save(*args, **kwargs)


class SolicitudServicio(models.Model):
    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)
    tipo_servicio = models.CharField(max_length=150)  # “Catering dulce para empresas”, etc.
    fecha_evento = models.DateField(null=True, blank=True)
    detalles = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f"{self.nombre} — {self.tipo_servicio} ({self.creado:%Y-%m-%d})"


