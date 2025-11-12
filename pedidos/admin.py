from django.contrib import admin
from .models import Pedido, LineaPedido

class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 0
    readonly_fields = ('nombre_producto', 'precio_unitario', 'cantidad', 'subtotal')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'email', 'total', 'estado', 'creado')
    list_filter = ('estado', 'creado')
    search_fields = ('nombre', 'email')
    inlines = [LineaPedidoInline]


