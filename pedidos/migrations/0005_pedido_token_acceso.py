import uuid

from django.db import migrations, models


def poblar_tokens_acceso(apps, schema_editor):
    Pedido = apps.get_model("pedidos", "Pedido")

    for pedido in Pedido.objects.filter(token_acceso__isnull=True):
        pedido.token_acceso = uuid.uuid4()
        pedido.save(update_fields=["token_acceso"])


class Migration(migrations.Migration):

    dependencies = [
        ("pedidos", "0004_historialestadopedido"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedido",
            name="token_acceso",
            field=models.UUIDField(db_index=True, editable=False, null=True),
        ),
        migrations.RunPython(
            poblar_tokens_acceso,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="pedido",
            name="token_acceso",
            field=models.UUIDField(
                db_index=True,
                default=uuid.uuid4,
                editable=False,
                unique=True,
            ),
        ),
    ]
