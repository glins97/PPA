from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from .event_manager import EventManager
from datetime import datetime, timedelta
from .notification_manager import send_mail
from PyPDF2 import PdfFileMerger
merger = PdfFileMerger()

events = [
    ('ON_ESSAY_UPLOAD', 'Upload de Redação'),
    ('ON_MONITOR_ASSIGNMENT', 'Determinação de Monitor'),
    ('ON_SINGLE_CORRECTION_DONE', 'Correção Completa'),
    ('ON_ALL_CORRECTIONS_DONE', 'Todas as Correções Completas'),
    ('ON_DELIVERY_DATE_ARRIVED', 'Data Final de Entrega Atingida'),
]

for event_code, event_name in events:
    EventManager.register_event(event_code)

send_target_modes = [
    ('MODE_STUDENT', 'Estudante'),
    ('MODE_SCHOOL', 'Escola'),
]

notification_modes = [
    ('MODE_MAIL', 'Email'),
]

MAX_REDACTIONS = 2
class School(models.Model):
    name = models.CharField(verbose_name='nome', max_length=256)
    state = models.CharField(verbose_name='estado', max_length=2) # TODO: ADD STATE CHOICES
    city = models.CharField(verbose_name='cidade', max_length=32) 
    email = models.CharField(verbose_name='email', max_length=256)
    days_to_redact = models.IntegerField(verbose_name='dias de correção', default=7)
    send_mode_target = models.CharField(verbose_name='enviar correções para', choices=send_target_modes, max_length=32)
    
    class Meta:
        verbose_name = 'escola'
        verbose_name_plural = 'escolas'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'Redação: ' + self.name

class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(verbose_name='nome', max_length=256)
    email = models.CharField(verbose_name='email', max_length=256)
    identification = models.CharField(verbose_name='matrícula', max_length=32)
    year = models.CharField(verbose_name='ano', max_length=2)
    class_id = models.CharField(verbose_name='turma', max_length=2)
    number_of_essays = models.IntegerField(verbose_name='número de redações', default=0)
    average_grade = models.IntegerField(verbose_name='nota média', default=0)
    
    class Meta:
        verbose_name = 'aluno'
        verbose_name_plural = 'alunos'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name

def essays_upload_to(essay, a):
    return 'uploads/essays/{}-{}-{}.pdf'.format(essay.student.name, essay.student.school.name, essay.upload_date)

def redactions_upload_to(redaction, a):
    return 'uploads/redactions/[CORRECAO]-{}-{}-{}.pdf'.format(redaction.essay.student.name, redaction.essay.student.school.name, redaction.essay.upload_date)

class Essay(models.Model):
    student = models.ForeignKey(Student, verbose_name='Aluno', on_delete=models.CASCADE)
    upload_date = models.DateField(verbose_name='data de submissão', blank=True, null=True)
    last_modified = models.DateField(verbose_name='última modificação', blank=True, null=True)
    delivery_date = models.DateField(verbose_name='data de entrega', blank=True, null=True)
    redactions = models.ManyToManyField('Redaction', related_name='redactions', verbose_name='correções', null=True, blank=True)
    last_redaction = models.ForeignKey('Redaction', related_name='last_redaction', editable=False, on_delete=models.CASCADE, blank=True, null=True)
    file = models.FileField(verbose_name='redação', upload_to=essays_upload_to, null=True, blank=True)
    final_grade = models.IntegerField(verbose_name='nota final', default=0)
    has_essay = models.BooleanField(editable=False, default=False, verbose_name='possui redação')
    sent = models.BooleanField(default=False, verbose_name='enviado')
    monitor_1 = models.ForeignKey(User, related_name='monitor_1', on_delete=models.CASCADE, blank=True, null=True)
    monitor_2 = models.ForeignKey(User, related_name='monitor_2', on_delete=models.CASCADE, blank=True, null=True)
    has_correction = models.BooleanField(default=False, verbose_name='correção finalizada')
    has_monitor_1 = models.BooleanField(editable=False, default=False)
    has_monitor_2 = models.BooleanField(editable=False, default=False)
    triage_done = models.BooleanField(editable=False, default=False)

    class Meta:
        ordering = ('last_modified', 'has_essay', '-has_correction')
        verbose_name = 'redação'
        verbose_name_plural = 'redações'

    def add_redaction(self, redaction):
        self.redactions.add(redaction)
        self.last_redaction = redaction
        self.final_grade = 0
        for redaction in self.redactions.all():
            self.final_grade += redaction.grades_average
        self.final_grade = self.final_grade / len(self.redactions.all())
        
        if len(self.redactions.all()) >= MAX_REDACTIONS:
            self.has_correction = True
        
        self.save()
    
    def do_triage(self):
        if self.file:
            self.triage_done = True
            merger = PdfFileMerger()
            merger.append(self.file)
            merger.append('essay/inputs/MODEL.pdf')
            merger.write(str(self.file).replace('.pdf', '_.pdf'))
            merger.close()
            self.file = str(self.file).replace('.pdf', '_.pdf')

    def save(self, *args, **kwargs):
        if not self.triage_done:
            super().save(*args, **kwargs)
            self.do_triage()

        self.last_modified = timezone.now()
        if not self.id:
            self.upload_date = self.last_modified
            self.delivery_date = self.last_modified + timedelta(days=self.student.school.days_to_redact)
        if not self.has_essay:
            self.has_essay = True
            EventManager.dispatch_event('ON_ESSAY_UPLOAD', self)
        if self.has_correction:
            EventManager.dispatch_event('ON_ALL_CORRECTIONS_DONE', self.last_redaction.file)
        if not self.has_monitor_1 and self.monitor_1:
            self.has_monitor_1 = True
            EventManager.dispatch_event('ON_MONITOR_ASSIGNMENT', self)
        if not self.has_monitor_2 and self.monitor_2:
            self.has_monitor_2 = True
            EventManager.dispatch_event('ON_MONITOR_ASSIGNMENT', self)
        essays = Essay.objects.all().filter(student__pk=self.student.pk)
        if essays:
            total_grade = sum([essay.final_grade for essay in essays])
            self.student.number_of_essays = len(essays)
            self.student.average_grade = total_grade * 1.0 / len(essays)
            self.student.save()
            
        super().save(*args, **kwargs)
        
    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.student)

class Redaction(models.Model):
    essay = models.ForeignKey(Essay, on_delete=models.CASCADE)
    monitor = models.ForeignKey(User, on_delete=models.CASCADE)
    grade_1 = models.IntegerField(verbose_name='competência 1', default=0)
    grade_2 = models.IntegerField(verbose_name='competência 2', default=0)
    grade_3 = models.IntegerField(verbose_name='competência 3', default=0)
    grade_4 = models.IntegerField(verbose_name='competência 4', default=0)
    grade_5 = models.IntegerField(verbose_name='competência 5', default=0)
    grades_average = models.IntegerField(verbose_name='nota', default=0, editable=False)
    date = models.DateTimeField(verbose_name='data de correção', blank=True, null=True, editable=False)
    file = models.FileField(verbose_name='correção', upload_to=redactions_upload_to, null=True, blank=True)

    class Meta:
        verbose_name = 'correção'
        verbose_name_plural = 'correções'

    def save(self, *args, **kwargs):
        self.essay.last_modified = timezone.now()
        self.date = timezone.now()
        self.grades_average = 0
        self.grades_average += self.grade_1
        self.grades_average += self.grade_2
        self.grades_average += self.grade_3
        self.grades_average += self.grade_4
        self.grades_average += self.grade_5
        super().save(*args, **kwargs)         
        EventManager.dispatch_event('ON_SINGLE_CORRECTION_DONE', self.essay, file=self.file)
        self.essay.add_redaction(self)


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{}: {}'.format(self.monitor, self.grades_average)

class NotificationConfiguration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mode = models.CharField(verbose_name='plataforma', choices=notification_modes, max_length=32)
    event = models.CharField(verbose_name='evento', choices=events, max_length=32)
    
    class Meta:
        verbose_name = 'notificação'
        verbose_name_plural = 'notificações'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{}: {} | {}'.format(self.user, self.mode, self.event)
