from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Servicio, SolicitudServicio


class SolicitudServicioTests(TestCase):
    def test_solicitud_guarda_servicio_y_tipo_servicio(self):
        servicio = Servicio.objects.create(
            titulo="Mesa dulce",
            slug="mesa-dulce",
            activo=True,
        )

        respuesta = self.client.post(
            reverse("servicios:solicitar_servicio", kwargs={"slug": servicio.slug}),
            data={
                "nombre": "Cliente Demo",
                "email": "cliente@example.com",
                "telefono": "809-000-0000",
                "fecha_evento": timezone.localdate().isoformat(),
                "detalles": "Para 20 personas",
            },
        )

        self.assertRedirects(
            respuesta,
            reverse("servicios:gracias", kwargs={"slug": servicio.slug}),
        )

        solicitud = SolicitudServicio.objects.get()
        self.assertEqual(solicitud.servicio, servicio)
        self.assertEqual(solicitud.tipo_servicio, servicio.titulo)
