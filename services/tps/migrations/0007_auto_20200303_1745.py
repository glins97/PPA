# Generated by Django 3.0.3 on 2020-03-03 20:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tps', '0006_tps_discipline'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tps',
            options={'ordering': ('name',), 'verbose_name': 'TPS', 'verbose_name_plural': 'TPS'},
        ),
    ]