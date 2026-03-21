from django.db import models
from django.utils.text import slugify


def generar_slug_unico(modelo, texto, instance_id=None):
    base_slug = slugify(texto)
    slug = base_slug
    contador = 1

    while modelo.objects.filter(slug=slug).exclude(id=instance_id).exists():
        slug = f"{base_slug}-{contador}"
        contador += 1

    return slug


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, null=True, blank=True)
    activa = models.BooleanField(default=True)
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def save(self, *args, **kwargs):
        if not self.slug and self.nombre:
            self.slug = generar_slug_unico(Categoria, self.nombre, self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos"
    )
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, null=True, blank=True)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to="tienda", null=True, blank=True)
    disponible = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["-creado", "nombre"]

    def save(self, *args, **kwargs):
        if not self.slug and self.nombre:
            self.slug = generar_slug_unico(Producto, self.nombre, self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre