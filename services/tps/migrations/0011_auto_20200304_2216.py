# Generated by Django 3.0.3 on 2020-03-05 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tps', '0010_auto_20200303_1808'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='correct_answer_1',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_10',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_2',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_3',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_4',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_5',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_6',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_7',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_8',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
        migrations.AddField(
            model_name='report',
            name='correct_answer_9',
            field=models.CharField(choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')], default='', max_length=1),
        ),
    ]
