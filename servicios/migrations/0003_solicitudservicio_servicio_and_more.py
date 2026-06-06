from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("servicios", "0002_solicitudservicio_alter_servicio_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="solicitudservicio",
            name="servicio",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="solicitudes",
                to="servicios.servicio",
            ),
        ),
        migrations.AlterField(
            model_name="solicitudservicio",
            name="tipo_servicio",
            field=models.CharField(blank=True, max_length=150),
        ),
    ]
