# carrito/carrito.py
from decimal import Decimal

class Carrito:
    def __init__(self, request):
        self.session = request.session
        self.carrito = self.session.get("carrito", {})

    def _id(self, producto):
        return str(producto.id)

    def guardar(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def agregar(self, producto):
        pid = self._id(producto)
        if pid not in self.carrito:
            self.carrito[pid] = {
                "producto_id": producto.id,
                "nombre": producto.nombre,
                "precio": str(producto.precio),  # guardamos como str para serializar
                "cantidad": 1,
            }
        else:
            self.carrito[pid]["cantidad"] += 1
        self.guardar()

    def restar(self, producto):
        pid = self._id(producto)
        if pid in self.carrito:
            self.carrito[pid]["cantidad"] -= 1
            if self.carrito[pid]["cantidad"] <= 0:
                del self.carrito[pid]
            self.guardar()

    def eliminar(self, producto):
        pid = self._id(producto)
        if pid in self.carrito:
            del self.carrito[pid]
            self.guardar()

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True

    def total(self):
        total = Decimal("0.00")
        for it in self.carrito.values():
            total += Decimal(it["precio"]) * it["cantidad"]
        return total
