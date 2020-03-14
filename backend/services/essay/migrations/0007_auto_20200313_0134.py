# Generated by Django 3.0.3 on 2020-03-13 04:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('essay', '0006_auto_20200313_0125'),
    ]

    operations = [
        migrations.AddField(
            model_name='essay',
            name='has_monitor_1',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='essay',
            name='has_monitor_2',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AddField(
            model_name='essay',
            name='monitor_1',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='monitor_1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='essay',
            name='monitor_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='monitor_2', to=settings.AUTH_USER_MODEL),
        ),
    ]
