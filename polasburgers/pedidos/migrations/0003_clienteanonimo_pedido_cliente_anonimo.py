# Generated by Django 5.1.6 on 2025-02-28 16:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0002_remove_producto_categoria_delete_categoria'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClienteAnonimo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=200)),
                ('direccion', models.TextField()),
                ('telefono', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='pedido',
            name='cliente_anonimo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='pedidos.clienteanonimo'),
        ),
    ]
