from django.db import models
from django.conf import settings
from tienda.models import Producto


class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        CONFIRMADO = "confirmado", "Confirmado"
        ENTREGADO = "entregado", "Entregado"
        CANCELADO = "cancelado", "Cancelado"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pedidos",
    )

    nombre = models.CharField(max_length=120)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.TextField(blank=True)

    fecha_evento = models.DateField(null=True, blank=True)
    detalles = models.TextField(blank=True)

    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )

    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return f"{self.codigo_pedido} – {self.nombre}"

    @property
    def codigo_pedido(self):
        if not self.pk:
            return "Pedido sin guardar"
        return f"DC-{self.pk:04d}-{self.creado.year}"

    @property
    def cantidad_total_productos(self):
        return sum(linea.cantidad for linea in self.lineas.all())

    @property
    def total_lineas(self):
        return self.lineas.count()

    @property
    def tiene_lineas(self):
        return self.lineas.exists()

    @property
    def badge_class(self):
        mapa = {
            self.Estado.PENDIENTE: "text-bg-warning",
            self.Estado.CONFIRMADO: "text-bg-info",
            self.Estado.ENTREGADO: "text-bg-success",
            self.Estado.CANCELADO: "text-bg-danger",
        }
        return mapa.get(self.estado, "text-bg-secondary")

    def puede_cambiar_a(self, nuevo_estado):
        transiciones_validas = {
            self.Estado.PENDIENTE: {
                self.Estado.CONFIRMADO,
                self.Estado.CANCELADO,
            },
            self.Estado.CONFIRMADO: {
                self.Estado.ENTREGADO,
                self.Estado.CANCELADO,
            },
            self.Estado.ENTREGADO: set(),
            self.Estado.CANCELADO: set(),
        }
        return nuevo_estado in transiciones_validas.get(self.estado, set())

    def registrar_cambio_estado(self, nuevo_estado, usuario=None, nota=""):
        estado_anterior = self.estado

        if estado_anterior == nuevo_estado:
            return None

        self.estado = nuevo_estado
        self.save(update_fields=["estado"])

        return HistorialEstadoPedido.objects.create(
            pedido=self,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            nota=nota,
            cambiado_por=usuario,
        )


class LineaPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        related_name="lineas",
        on_delete=models.CASCADE,
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    nombre_producto = models.CharField(max_length=200)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Línea de pedido"
        verbose_name_plural = "Líneas de pedido"

    def __str__(self):
        return f"{self.nombre_producto} x {self.cantidad}"

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


class HistorialEstadoPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        related_name="historial_estados",
        on_delete=models.CASCADE,
    )
    estado_anterior = models.CharField(max_length=20, choices=Pedido.Estado.choices)
    estado_nuevo = models.CharField(max_length=20, choices=Pedido.Estado.choices)
    nota = models.TextField(blank=True)
    cambiado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cambios_estado_pedidos",
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Historial de estado del pedido"
        verbose_name_plural = "Historial de estados de pedidos"

    def __str__(self):
        return f"{self.pedido.codigo_pedido}: {self.estado_anterior} → {self.estado_nuevo}"