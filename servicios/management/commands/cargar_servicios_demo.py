from decimal import Decimal

from django.core.management.base import BaseCommand

from servicios.models import Servicio


DEMO_SERVICES = [
    {
        "titulo": "Mesa dulce para eventos",
        "slug": "mesa-dulce-para-eventos",
        "descripcion": (
            "Servicio de mesa dulce personalizada para cumpleanos, reuniones "
            "familiares y celebraciones pequenas."
        ),
        "precio_desde": "2500.00",
    },
    {
        "titulo": "Bizcochos personalizados",
        "slug": "bizcochos-personalizados",
        "descripcion": (
            "Bizcochos decorados segun la ocasion, con sabores y detalles "
            "adaptados al estilo del evento."
        ),
        "precio_desde": "1800.00",
    },
    {
        "titulo": "Detalles dulces para regalar",
        "slug": "detalles-dulces-para-regalar",
        "descripcion": (
            "Cajas y arreglos de postres artesanales preparados para regalos, "
            "agradecimientos y fechas especiales."
        ),
        "precio_desde": "950.00",
    },
]


class Command(BaseCommand):
    help = "Crea servicios demo para probar la seccion de servicios."

    def handle(self, *args, **options):
        creados = 0
        actualizados = 0

        for servicio_data in DEMO_SERVICES:
            servicio, created = Servicio.objects.update_or_create(
                slug=servicio_data["slug"],
                defaults={
                    "titulo": servicio_data["titulo"],
                    "descripcion": servicio_data["descripcion"],
                    "precio_desde": Decimal(servicio_data["precio_desde"]),
                    "activo": True,
                },
            )

            if created:
                creados += 1
            else:
                actualizados += 1

        self.stdout.write(self.style.SUCCESS("Servicios demo cargados correctamente."))
        self.stdout.write(f"Servicios: {creados} creados, {actualizados} actualizados.")
