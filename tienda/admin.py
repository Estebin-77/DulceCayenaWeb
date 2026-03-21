from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "slug", "activa", "creada", "actualizada")
    list_filter = ("activa", "creada", "actualizada")
    search_fields = ("nombre", "slug")
    prepopulated_fields = {"slug": ("nombre",)}
    readonly_fields = ("creada", "actualizada")
    ordering = ("nombre",)
    list_per_page = 20
    empty_value_display = "—"

    fieldsets = (
        ("Información principal", {
            "fields": ("nombre", "slug", "activa")
        }),
        ("Fechas", {
            "fields": ("creada", "actualizada")
        }),
    )


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "miniatura",
        "nombre",
        "categoria",
        "precio",
        "disponible",
        "destacado",
        "creado",
        "actualizado",
    )
    list_filter = ("disponible", "destacado", "categoria", "creado", "actualizado")
    search_fields = ("nombre", "slug", "descripcion")
    prepopulated_fields = {"slug": ("nombre",)}
    readonly_fields = ("creado", "actualizado", "miniatura_preview")
    list_editable = ("precio", "disponible", "destacado")
    ordering = ("-creado", "nombre")
    list_per_page = 20
    empty_value_display = "—"

    fieldsets = (
        ("Información principal", {
            "fields": ("nombre", "slug", "categoria", "descripcion")
        }),
        ("Precio e imagen", {
            "fields": ("precio", "imagen", "miniatura_preview")
        }),
        ("Estado", {
            "fields": ("disponible", "destacado")
        }),
        ("Fechas", {
            "fields": ("creado", "actualizado")
        }),
    )

    def miniatura(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="width:60px; height:60px; object-fit:cover; border-radius:8px;" />',
                obj.imagen.url
            )
        return "Sin imagen"
    miniatura.short_description = "Imagen"

    def miniatura_preview(self, obj):
        if obj.imagen:
            return format_html(
                '<img src="{}" style="max-width:220px; border-radius:12px; box-shadow:0 2px 8px rgba(0,0,0,.15);" />',
                obj.imagen.url
            )
        return "Este producto no tiene imagen."
    miniatura_preview.short_description = "Vista previa"