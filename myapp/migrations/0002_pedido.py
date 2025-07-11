# Generated by Django 5.1.7 on 2025-06-05 16:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('paypal_order_id', models.CharField(max_length=100, unique=True)),
                ('paypal_capture_id', models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ('monto_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('moneda', models.CharField(default='USD', max_length=10)),
                ('estado', models.CharField(choices=[('PENDIENTE', 'Pendiente'), ('COMPLETADO', 'Completado'), ('FALLIDO', 'Fallido'), ('REEMBOLSADO', 'Reembolsado')], default='PENDIENTE', max_length=20)),
                ('payer_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('payer_id_paypal', models.CharField(blank=True, max_length=100, null=True)),
                ('payer_nombre', models.CharField(blank=True, max_length=200, null=True)),
                ('fecha_creacion_pedido', models.DateTimeField(auto_now_add=True)),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True)),
                ('producto', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='myapp.producto')),
                ('registro_usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pedidos', to='myapp.registro')),
            ],
            options={
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
                'ordering': ['-fecha_creacion_pedido'],
            },
        ),
    ]
