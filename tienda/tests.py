from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from .models import Categoria, Producto


class CargarProductosDemoCommandTests(TestCase):
    def test_crea_catalogo_demo(self):
        out = StringIO()

        call_command("cargar_productos_demo", stdout=out)

        self.assertEqual(Categoria.objects.count(), 3)
        self.assertEqual(Producto.objects.count(), 7)
        self.assertEqual(Producto.objects.filter(disponible=True).count(), 7)
        self.assertGreaterEqual(Producto.objects.filter(destacado=True).count(), 1)
        self.assertIn("Catalogo demo cargado correctamente", out.getvalue())

    def test_no_duplica_datos_al_ejecutarse_dos_veces(self):
        call_command("cargar_productos_demo", stdout=StringIO())
        call_command("cargar_productos_demo", stdout=StringIO())

        self.assertEqual(Categoria.objects.count(), 3)
        self.assertEqual(Producto.objects.count(), 7)
