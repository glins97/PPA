# Generated by Django 3.0.3 on 2020-03-13 04:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('essay', '0007_auto_20200313_0134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='essay',
            name='has_correction',
            field=models.BooleanField(default=False, verbose_name='correção finalizada'),
        ),
    ]
