from django.contrib import admin
from .models import Servicio, SolicitudServicio

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activo', 'creado')
    list_filter = ('activo', 'creado')
    search_fields = ('titulo', 'descripcion')
    prepopulated_fields = {"slug": ("titulo",)}  # útil al cargar desde admin

@admin.register(SolicitudServicio)
class SolicitudServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'servicio', 'tipo_servicio', 'fecha_evento', 'email', 'creado')
    list_filter = ('servicio', 'fecha_evento', 'creado')
    search_fields = ('nombre', 'email', 'telefono', 'tipo_servicio', 'servicio__titulo', 'detalles')
