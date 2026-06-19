from django.test import TestCase
from django.test import Client
from django.urls import reverse

from tienda.models import Producto


class CarritoMetodoSeguroTests(TestCase):
    def setUp(self):
        self.producto = Producto.objects.create(
            nombre="Dulce de prueba",
            descripcion="Producto para pruebas del carrito",
            precio="100.00",
            disponible=True,
        )
        self.url_agregar = reverse(
            "carrito:agregar_al_carrito",
            kwargs={"producto_id": self.producto.id},
        )

    def test_get_no_agrega_producto_al_carrito(self):
        response = self.client.get(self.url_agregar)

        self.assertEqual(response.status_code, 405)
        self.assertNotIn("carrito", self.client.session)

    def test_post_agrega_producto_al_carrito(self):
        response = self.client.post(
            self.url_agregar,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 200)
        carrito = self.client.session["carrito"]
        self.assertEqual(carrito[str(self.producto.id)]["cantidad"], 1)

    def test_post_sin_csrf_es_rechazado_cuando_csrf_esta_activo(self):
        csrf_client = Client(enforce_csrf_checks=True)

        response = csrf_client.post(
            self.url_agregar,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        self.assertEqual(response.status_code, 403)
