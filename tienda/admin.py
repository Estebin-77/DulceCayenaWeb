from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'disponible', 'creado', 'actualizado')
    list_filter = ('disponible',)
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('creado', 'actualizado')
