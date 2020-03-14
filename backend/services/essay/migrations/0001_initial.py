# Generated by Django 3.0.3 on 2020-03-13 01:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Essay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('upload_date', models.DateTimeField(blank=True, null=True, verbose_name='data de submissão')),
                ('last_modified', models.DateTimeField(blank=True, null=True, verbose_name='última modificação')),
                ('delivery_date', models.DateTimeField(blank=True, null=True, verbose_name='data de entrega')),
                ('file', models.FileField(blank=True, null=True, upload_to='uploads/essays', verbose_name='redação')),
                ('has_essay', models.BooleanField(default=False, editable=False, verbose_name='possui redação')),
                ('has_correction', models.BooleanField(default=False, editable=False, verbose_name='possui correção')),
                ('final_grade', models.IntegerField(blank=True, editable=False, null=True, verbose_name='nota final')),
            ],
            options={
                'verbose_name': 'redação',
                'verbose_name_plural': 'redações',
                'ordering': ('last_modified', 'has_essay', '-has_correction'),
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='escola')),
                ('state', models.CharField(max_length=2, verbose_name='estado')),
                ('city', models.CharField(max_length=32, verbose_name='cidade')),
                ('email', models.CharField(max_length=256, verbose_name='email')),
                ('days_to_redact', models.IntegerField(default=7, verbose_name='dias de correção')),
                ('send_mode_target', models.CharField(choices=[('MODE_STUDENT', 'Estudante'), ('MODE_SCHOOL', 'Escola')], max_length=32, verbose_name='enviar correções para')),
                ('send_mode_quantity', models.CharField(choices=[('MODE_ONE', 'Uma'), ('MODE_ALL', 'Todas')], max_length=32, verbose_name='quantidade')),
            ],
            options={
                'verbose_name': 'escola',
                'verbose_name_plural': 'escolas',
            },
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='aluno')),
                ('email', models.CharField(max_length=256, verbose_name='email')),
                ('identification', models.CharField(max_length=32, verbose_name='matrícula')),
                ('year', models.CharField(max_length=2, verbose_name='ano')),
                ('class_id', models.CharField(max_length=2, verbose_name='turma')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='essay.School')),
            ],
            options={
                'verbose_name': 'aluno',
                'verbose_name_plural': 'alunos',
            },
        ),
        migrations.CreateModel(
            name='Redaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade_1', models.IntegerField(default=0, editable=False, verbose_name='competência 1')),
                ('grade_2', models.IntegerField(default=0, editable=False, verbose_name='competência 2')),
                ('grade_3', models.IntegerField(default=0, editable=False, verbose_name='competência 3')),
                ('grade_4', models.IntegerField(default=0, editable=False, verbose_name='competência 4')),
                ('grade_5', models.IntegerField(default=0, editable=False, verbose_name='competência 5')),
                ('grades_average', models.IntegerField(blank=True, editable=False, null=True, verbose_name='nota')),
                ('date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='data de correção')),
                ('file', models.FileField(blank=True, null=True, upload_to='uploads/redactions', verbose_name='correção')),
                ('essay', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='essay.Essay')),
                ('monitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'correção',
                'verbose_name_plural': 'correções',
            },
        ),
        migrations.CreateModel(
            name='NotificationConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(choices=[('MODE_MAIL', 'Email'), ('MODE_PHONE', 'Celular')], max_length=32, verbose_name='plataforma')),
                ('event', models.CharField(choices=[('ON_ESSAY_UPLOAD', 'Upload de Redação'), ('ON_SINGLE_CORRECTION_DONE', 'Correção Completa'), ('ON_ALL_CRRECTIONS_DONE', 'Todas as Correções Completas'), ('ON_DELIVERY_DATE_ARRIVED', 'Data Final de Entrega Atingida')], max_length=32, verbose_name='evento')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'notificação',
                'verbose_name_plural': 'notificações',
            },
        ),
        migrations.AddField(
            model_name='essay',
            name='redactions',
            field=models.ManyToManyField(blank=True, null=True, related_name='redactions', to='essay.Redaction', verbose_name='correções'),
        ),
        migrations.AddField(
            model_name='essay',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='essay.Student'),
        ),
    ]
