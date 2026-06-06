from django.test import TestCase
from django.urls import reverse

from .models import Pedido


class PedidoPublicoTests(TestCase):
    def test_detalle_publico_usa_token_no_id(self):
        pedido = Pedido.objects.create(
            nombre="Cliente Demo",
            email="cliente@example.com",
            total="1200.00",
        )

        respuesta_por_id = self.client.get(f"/pedidos/detalle/{pedido.id}/")
        self.assertEqual(respuesta_por_id.status_code, 404)

        url_privada = reverse(
            "pedidos:detalle_publico",
            kwargs={"token_acceso": pedido.token_acceso},
        )
        respuesta_por_token = self.client.get(url_privada)
        self.assertEqual(respuesta_por_token.status_code, 200)

    def test_pdf_publico_usa_token_no_id(self):
        pedido = Pedido.objects.create(
            nombre="Cliente Demo",
            email="cliente@example.com",
            total="1200.00",
        )

        respuesta_por_id = self.client.get(f"/pedidos/descargar-pdf/{pedido.id}/")
        self.assertEqual(respuesta_por_id.status_code, 404)

        url_privada = reverse(
            "pedidos:descargar_pdf",
            kwargs={"token_acceso": pedido.token_acceso},
        )
        respuesta_por_token = self.client.get(url_privada)
        self.assertEqual(respuesta_por_token.status_code, 200)
        self.assertEqual(respuesta_por_token["Content-Type"], "application/pdf")
