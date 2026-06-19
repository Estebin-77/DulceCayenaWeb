from decimal import Decimal

from django.core.management.base import BaseCommand

from tienda.models import Categoria, Producto


DEMO_CATALOG = [
    {
        "nombre": "Postres Artesanales",
        "slug": "postres-artesanales",
        "productos": [
            {
                "nombre": "Dulce de Coco",
                "slug": "dulce-de-coco",
                "descripcion": (
                    "Dulce artesanal de coco preparado para compartir en porciones "
                    "individuales o como detalle especial."
                ),
                "precio": "100.00",
                "destacado": True,
            },
            {
                "nombre": "Brownie de Chocolate",
                "slug": "brownie-de-chocolate",
                "descripcion": (
                    "Brownie suave y humedo con intenso sabor a chocolate, ideal "
                    "para antojos y pedidos pequenos."
                ),
                "precio": "125.00",
                "destacado": True,
            },
            {
                "nombre": "Cupcake de Vainilla",
                "slug": "cupcake-de-vainilla",
                "descripcion": (
                    "Cupcake esponjoso de vainilla con cubierta dulce, pensado para "
                    "eventos, regalos y celebraciones."
                ),
                "precio": "90.00",
                "destacado": False,
            },
        ],
    },
    {
        "nombre": "Bocaditos Dulces",
        "slug": "bocaditos-dulces",
        "productos": [
            {
                "nombre": "Galletas de Mantequilla",
                "slug": "galletas-de-mantequilla",
                "descripcion": (
                    "Galletas crujientes de mantequilla, perfectas para meriendas, "
                    "mesas dulces y detalles personalizados."
                ),
                "precio": "75.00",
                "destacado": False,
            },
            {
                "nombre": "Trufas de Chocolate",
                "slug": "trufas-de-chocolate",
                "descripcion": (
                    "Bocaditos de chocolate con textura cremosa, listos para regalar "
                    "o acompanar celebraciones pequenas."
                ),
                "precio": "150.00",
                "destacado": True,
            },
        ],
    },
    {
        "nombre": "Bizcochos",
        "slug": "bizcochos",
        "productos": [
            {
                "nombre": "Bizcocho Tres Leches",
                "slug": "bizcocho-tres-leches",
                "descripcion": (
                    "Bizcocho clasico tres leches, suave y jugoso, recomendado para "
                    "cumpleanos y reuniones familiares."
                ),
                "precio": "850.00",
                "destacado": True,
            },
            {
                "nombre": "Mini Bizcocho de Zanahoria",
                "slug": "mini-bizcocho-de-zanahoria",
                "descripcion": (
                    "Mini bizcocho de zanahoria con especias suaves, ideal para "
                    "probar sabores o hacer pedidos pequenos."
                ),
                "precio": "450.00",
                "destacado": False,
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Crea categorias y productos demo para probar la tienda."

    def handle(self, *args, **options):
        categorias_creadas = 0
        categorias_actualizadas = 0
        productos_creados = 0
        productos_actualizados = 0

        for categoria_data in DEMO_CATALOG:
            categoria, created = Categoria.objects.update_or_create(
                slug=categoria_data["slug"],
                defaults={
                    "nombre": categoria_data["nombre"],
                    "activa": True,
                },
            )

            if created:
                categorias_creadas += 1
            else:
                categorias_actualizadas += 1

            for producto_data in categoria_data["productos"]:
                producto, created = Producto.objects.update_or_create(
                    slug=producto_data["slug"],
                    defaults={
                        "categoria": categoria,
                        "nombre": producto_data["nombre"],
                        "descripcion": producto_data["descripcion"],
                        "precio": Decimal(producto_data["precio"]),
                        "disponible": True,
                        "destacado": producto_data["destacado"],
                    },
                )

                if created:
                    productos_creados += 1
                else:
                    productos_actualizados += 1

        self.stdout.write(self.style.SUCCESS("Catalogo demo cargado correctamente."))
        self.stdout.write(
            (
                f"Categorias: {categorias_creadas} creadas, "
                f"{categorias_actualizadas} actualizadas."
            )
        )
        self.stdout.write(
            (
                f"Productos: {productos_creados} creados, "
                f"{productos_actualizados} actualizados."
            )
        )
