from django import forms
from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.timezone import localtime

from .models import Pedido, LineaPedido, HistorialEstadoPedido


class PedidoAdminForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = "__all__"

    def clean_estado(self):
        nuevo_estado = self.cleaned_data.get("estado")

        if not self.instance or not self.instance.pk:
            return nuevo_estado

        estado_actual = self.instance.estado

        if estado_actual == nuevo_estado:
            return nuevo_estado

        if not self.instance.puede_cambiar_a(nuevo_estado):
            raise forms.ValidationError(
                f"No se permite cambiar el estado de "
                f"'{self.instance.get_estado_display()}' a "
                f"'{dict(Pedido.Estado.choices).get(nuevo_estado, nuevo_estado)}'."
            )

        return nuevo_estado


def _badge_estado_admin(estado):
    colores = {
        Pedido.Estado.PENDIENTE: ("#fff3cd", "#856404"),
        Pedido.Estado.CONFIRMADO: ("#d1ecf1", "#0c5460"),
        Pedido.Estado.ENTREGADO: ("#d4edda", "#155724"),
        Pedido.Estado.CANCELADO: ("#f8d7da", "#721c24"),
    }
    fondo, texto = colores.get(estado, ("#e2e3e5", "#383d41"))
    etiqueta = dict(Pedido.Estado.choices).get(estado, estado)

    return format_html(
        '<span style="background:{}; color:{}; padding:4px 10px; '
        'border-radius:999px; font-weight:600; font-size:12px; '
        'display:inline-block;">{}</span>',
        fondo,
        texto,
        etiqueta,
    )


class LineaPedidoInline(admin.TabularInline):
    model = LineaPedido
    extra = 0
    can_delete = False
    max_num = 0
    readonly_fields = (
        "producto",
        "nombre_producto",
        "precio_unitario",
        "cantidad",
        "subtotal",
    )
    fields = (
        "producto",
        "nombre_producto",
        "precio_unitario",
        "cantidad",
        "subtotal",
    )
    verbose_name = "Línea del pedido"
    verbose_name_plural = "Productos del pedido"

    def has_add_permission(self, request, obj=None):
        return False


class HistorialEstadoPedidoInline(admin.TabularInline):
    model = HistorialEstadoPedido
    extra = 0
    can_delete = False
    max_num = 0

    readonly_fields = (
        "transicion_badges",
        "cambiado_por_admin",
        "creado_formateado",
        "nota_admin",
    )

    fields = (
        "transicion_badges",
        "cambiado_por_admin",
        "creado_formateado",
        "nota_admin",
    )

    verbose_name = "Cambio de estado"
    verbose_name_plural = "Historial de cambios de estado"

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def transicion_badges(self, obj):
        return format_html(
            '{} <span style="margin:0 8px; font-weight:700; color:#6c757d;">→</span> {}',
            _badge_estado_admin(obj.estado_anterior),
            _badge_estado_admin(obj.estado_nuevo),
        )
    transicion_badges.short_description = "Transición"

    def cambiado_por_admin(self, obj):
        if obj.cambiado_por:
            nombre = (
                obj.cambiado_por.get_full_name().strip()
                if hasattr(obj.cambiado_por, "get_full_name")
                else ""
            )
            if nombre:
                return f"{nombre} ({obj.cambiado_por.username})"
            return obj.cambiado_por.username
        return "Sistema"
    cambiado_por_admin.short_description = "Cambiado por"

    def creado_formateado(self, obj):
        fecha_local = localtime(obj.creado)
        return fecha_local.strftime("%d/%m/%Y %I:%M %p")
    creado_formateado.short_description = "Fecha"

    def nota_admin(self, obj):
        if obj.nota:
            return format_html(
                '<div style="white-space:pre-wrap; max-width:420px;">{}</div>',
                obj.nota,
            )
        return format_html('<span style="color:#6c757d;">Sin nota</span>')
    nota_admin.short_description = "Nota"


def _cambiar_estado_desde_admin(modeladmin, request, queryset, nuevo_estado):
    actualizados = 0
    omitidos = 0

    for pedido in queryset:
        if pedido.estado == nuevo_estado:
            omitidos += 1
            continue

        if not pedido.puede_cambiar_a(nuevo_estado):
            omitidos += 1
            continue

        cambio = pedido.registrar_cambio_estado(
            nuevo_estado=nuevo_estado,
            usuario=request.user,
            nota="Estado actualizado desde acciones del administrador.",
        )
        if cambio:
            actualizados += 1

    if actualizados:
        modeladmin.message_user(
            request,
            f"Se actualizaron {actualizados} pedido(s) y se registró su historial.",
            level=messages.SUCCESS,
        )

    if omitidos:
        modeladmin.message_user(
            request,
            f"Se omitieron {omitidos} pedido(s) porque ya tenían ese estado o la transición no está permitida.",
            level=messages.WARNING,
        )

    if actualizados == 0 and omitidos == 0:
        modeladmin.message_user(
            request,
            "No se realizaron cambios.",
            level=messages.INFO,
        )


@admin.action(description="Marcar pedidos seleccionados como pendientes")
def marcar_como_pendiente(modeladmin, request, queryset):
    _cambiar_estado_desde_admin(
        modeladmin,
        request,
        queryset,
        Pedido.Estado.PENDIENTE,
    )


@admin.action(description="Marcar pedidos seleccionados como confirmados")
def marcar_como_confirmado(modeladmin, request, queryset):
    _cambiar_estado_desde_admin(
        modeladmin,
        request,
        queryset,
        Pedido.Estado.CONFIRMADO,
    )


@admin.action(description="Marcar pedidos seleccionados como entregados")
def marcar_como_entregado(modeladmin, request, queryset):
    _cambiar_estado_desde_admin(
        modeladmin,
        request,
        queryset,
        Pedido.Estado.ENTREGADO,
    )


@admin.action(description="Marcar pedidos seleccionados como cancelados")
def marcar_como_cancelado(modeladmin, request, queryset):
    _cambiar_estado_desde_admin(
        modeladmin,
        request,
        queryset,
        Pedido.Estado.CANCELADO,
    )


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    form = PedidoAdminForm

    list_display = (
        "id",
        "codigo_admin",
        "nombre",
        "email",
        "telefono",
        "cantidad_productos_admin",
        "total_lineas_admin",
        "total",
        "estado_badge",
        "fecha_evento",
        "creado",
    )
    list_display_links = ("id", "codigo_admin", "nombre")
    list_filter = ("estado", "creado", "fecha_evento")
    search_fields = (
        "nombre",
        "email",
        "telefono",
        "direccion",
        "detalles",
        "id",
    )
    ordering = ("-id",)
    date_hierarchy = "creado"
    list_per_page = 20
    empty_value_display = "—"

    readonly_fields = (
        "resumen_general",
        "usuario",
        "codigo_admin_detalle",
        "cantidad_productos_admin",
        "total_lineas_admin",
        "tiene_lineas_admin",
        "total",
        "creado",
        "estado_badge_detalle",
        "cliente_resumen",
        "pedido_resumen",
    )

    fieldsets = (
        (
            "Resumen rápido",
            {
                "fields": (
                    "resumen_general",
                )
            },
        ),
        (
            "Control del pedido",
            {
                "fields": (
                    "codigo_admin_detalle",
                    "estado",
                    "estado_badge_detalle",
                    "creado",
                )
            },
        ),
        (
            "Resumen del cliente",
            {
                "fields": (
                    "cliente_resumen",
                )
            },
        ),
        (
            "Datos del cliente",
            {
                "fields": (
                    "usuario",
                    "nombre",
                    "email",
                    "telefono",
                    "direccion",
                )
            },
        ),
        (
            "Resumen del pedido",
            {
                "fields": (
                    "pedido_resumen",
                )
            },
        ),
        (
            "Datos del pedido",
            {
                "fields": (
                    "fecha_evento",
                    "detalles",
                    "cantidad_productos_admin",
                    "total_lineas_admin",
                    "tiene_lineas_admin",
                    "total",
                )
            },
        ),
    )

    inlines = [LineaPedidoInline, HistorialEstadoPedidoInline]

    actions = (
        marcar_como_pendiente,
        marcar_como_confirmado,
        marcar_como_entregado,
        marcar_como_cancelado,
    )

    def save_model(self, request, obj, form, change):
        estado_anterior = None

        if change and obj.pk:
            estado_anterior = Pedido.objects.get(pk=obj.pk).estado

        super().save_model(request, obj, form, change)

        if change and estado_anterior and estado_anterior != obj.estado:
            HistorialEstadoPedido.objects.create(
                pedido=obj,
                estado_anterior=estado_anterior,
                estado_nuevo=obj.estado,
                nota="Estado actualizado desde el formulario del administrador.",
                cambiado_por=request.user,
            )

    def codigo_admin(self, obj):
        return obj.codigo_pedido
    codigo_admin.short_description = "Código"

    def codigo_admin_detalle(self, obj):
        return obj.codigo_pedido
    codigo_admin_detalle.short_description = "Código del pedido"

    def cantidad_productos_admin(self, obj):
        return obj.cantidad_total_productos
    cantidad_productos_admin.short_description = "Productos"

    def total_lineas_admin(self, obj):
        return obj.total_lineas
    total_lineas_admin.short_description = "Líneas"

    def tiene_lineas_admin(self, obj):
        if obj.tiene_lineas:
            return format_html(
                '<span style="color:#155724; font-weight:600;">Sí</span>'
            )
        return format_html(
            '<span style="color:#721c24; font-weight:600;">No</span>'
        )
    tiene_lineas_admin.short_description = "¿Tiene líneas?"

    def estado_badge(self, obj):
        return _badge_estado_admin(obj.estado)
    estado_badge.short_description = "Estado"

    def estado_badge_detalle(self, obj):
        return self.estado_badge(obj)
    estado_badge_detalle.short_description = "Vista rápida del estado"

    def resumen_general(self, obj):
        if not obj or not obj.pk:
            return "El resumen estará disponible cuando el pedido se haya guardado."

        return format_html(
            """
            <div style="display:flex; flex-wrap:wrap; gap:12px; margin:6px 0 2px 0;">
                <div style="background:#f8f9fa; border:1px solid #e9ecef; border-radius:12px; padding:12px 14px; min-width:180px;">
                    <div style="font-size:12px; color:#6c757d; margin-bottom:4px;">Código</div>
                    <div style="font-weight:700;">{}</div>
                </div>
                <div style="background:#f8f9fa; border:1px solid #e9ecef; border-radius:12px; padding:12px 14px; min-width:180px;">
                    <div style="font-size:12px; color:#6c757d; margin-bottom:4px;">Estado</div>
                    <div>{}</div>
                </div>
                <div style="background:#f8f9fa; border:1px solid #e9ecef; border-radius:12px; padding:12px 14px; min-width:180px;">
                    <div style="font-size:12px; color:#6c757d; margin-bottom:4px;">Total</div>
                    <div style="font-weight:700;">RD$ {}</div>
                </div>
                <div style="background:#f8f9fa; border:1px solid #e9ecef; border-radius:12px; padding:12px 14px; min-width:180px;">
                    <div style="font-size:12px; color:#6c757d; margin-bottom:4px;">Productos</div>
                    <div style="font-weight:700;">{}</div>
                </div>
                <div style="background:#f8f9fa; border:1px solid #e9ecef; border-radius:12px; padding:12px 14px; min-width:180px;">
                    <div style="font-size:12px; color:#6c757d; margin-bottom:4px;">Líneas</div>
                    <div style="font-weight:700;">{}</div>
                </div>
            </div>
            """,
            obj.codigo_pedido,
            self.estado_badge(obj),
            obj.total,
            obj.cantidad_total_productos,
            obj.total_lineas,
        )
    resumen_general.short_description = "Vista general"

    def cliente_resumen(self, obj):
        if not obj or not obj.pk:
            return "El resumen del cliente estará disponible cuando el pedido se haya guardado."

        direccion = obj.direccion if obj.direccion else "Sin dirección registrada"
        telefono = obj.telefono if obj.telefono else "Sin teléfono registrado"

        return format_html(
            """
            <div style="line-height:1.7;">
                <div><strong>Cliente:</strong> {}</div>
                <div><strong>Email:</strong> {}</div>
                <div><strong>Teléfono:</strong> {}</div>
                <div><strong>Dirección:</strong> {}</div>
            </div>
            """,
            obj.nombre,
            obj.email,
            telefono,
            direccion,
        )
    cliente_resumen.short_description = "Resumen del cliente"

    def pedido_resumen(self, obj):
        if not obj or not obj.pk:
            return "El resumen del pedido estará disponible cuando el pedido se haya guardado."

        fecha_evento = obj.fecha_evento.strftime("%d/%m/%Y") if obj.fecha_evento else "No definida"
        detalles = obj.detalles if obj.detalles else "Sin detalles adicionales"

        return format_html(
            """
            <div style="line-height:1.7;">
                <div><strong>Fecha del evento:</strong> {}</div>
                <div><strong>Tiene líneas:</strong> {}</div>
                <div><strong>Total de líneas:</strong> {}</div>
                <div><strong>Total de productos:</strong> {}</div>
                <div><strong>Detalles:</strong><br><div style="margin-top:4px; white-space:pre-wrap;">{}</div></div>
            </div>
            """,
            fecha_evento,
            self.tiene_lineas_admin(obj),
            obj.total_lineas,
            obj.cantidad_total_productos,
            detalles,
        )
    pedido_resumen.short_description = "Resumen del pedido"


@admin.register(HistorialEstadoPedido)
class HistorialEstadoPedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "pedido_codigo",
        "pedido_cliente",
        "transicion_badges",
        "cambiado_por_admin",
        "creado_formateado",
    )
    list_display_links = ("id", "pedido_codigo")
    list_filter = (
        "estado_anterior",
        "estado_nuevo",
        "cambiado_por",
        "creado",
    )
    search_fields = (
        "pedido__id",
        "pedido__nombre",
        "pedido__email",
        "pedido__telefono",
        "cambiado_por__username",
        "cambiado_por__first_name",
        "cambiado_por__last_name",
        "nota",
    )
    ordering = ("-creado",)
    date_hierarchy = "creado"
    list_per_page = 25
    empty_value_display = "—"

    readonly_fields = (
        "pedido",
        "pedido_codigo",
        "pedido_cliente",
        "transicion_badges",
        "estado_anterior",
        "estado_nuevo",
        "cambiado_por",
        "creado_formateado",
        "nota_admin",
    )

    fields = (
        "pedido",
        "pedido_codigo",
        "pedido_cliente",
        "transicion_badges",
        "cambiado_por",
        "creado_formateado",
        "nota_admin",
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def pedido_codigo(self, obj):
        return obj.pedido.codigo_pedido
    pedido_codigo.short_description = "Código pedido"

    def pedido_cliente(self, obj):
        return f"{obj.pedido.nombre} • {obj.pedido.email}"
    pedido_cliente.short_description = "Cliente"

    def transicion_badges(self, obj):
        return format_html(
            '{} <span style="margin:0 8px; font-weight:700; color:#6c757d;">→</span> {}',
            _badge_estado_admin(obj.estado_anterior),
            _badge_estado_admin(obj.estado_nuevo),
        )
    transicion_badges.short_description = "Transición"

    def cambiado_por_admin(self, obj):
        if obj.cambiado_por:
            nombre = (
                obj.cambiado_por.get_full_name().strip()
                if hasattr(obj.cambiado_por, "get_full_name")
                else ""
            )
            if nombre:
                return f"{nombre} ({obj.cambiado_por.username})"
            return obj.cambiado_por.username
        return "Sistema"
    cambiado_por_admin.short_description = "Cambiado por"

    def creado_formateado(self, obj):
        fecha_local = localtime(obj.creado)
        return fecha_local.strftime("%d/%m/%Y %I:%M %p")
    creado_formateado.short_description = "Fecha"

    def nota_admin(self, obj):
        if obj.nota:
            return format_html(
                '<div style="white-space:pre-wrap; max-width:700px;">{}</div>',
                obj.nota,
            )
        return format_html('<span style="color:#6c757d;">Sin nota</span>')
    nota_admin.short_description = "Nota"