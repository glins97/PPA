from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone

import requests
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from threading import _start_new_thread
def _email_notify(content, email, student_name):
    if not content:
        return
    
    msg = MIMEMultipart()
    message = 'Thank you'

    password = 'qazxsaq01'
    msg['To'] = email
    msg['From'] = 'adm.ppa.digital@gmail.com'
    msg['Subject'] = 'PPA Digital: ' + student_name
    
    msg.attach(MIMEText(content, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()

class NotificationMode(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    name = models.CharField(verbose_name='nome', max_length=256)
    description = models.TextField(verbose_name='descrição')

    class Meta:
        verbose_name = 'LOOKUP_MODE'
        verbose_name_plural = 'LOOKUP_MODES'

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class NotificationTiming(models.Model):
    id = models.CharField(primary_key=True, max_length=256)
    name = models.CharField(verbose_name='nome', max_length=256)
    description = models.TextField(verbose_name='descrição')

    class Meta:
        verbose_name = 'LOOKUP_TIMING'
        verbose_name_plural = 'LOOKUP_TIMINGS'

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class NotificationConfiguration(models.Model):
    user = models.ForeignKey(User, verbose_name='usuário', null=True, blank=True, on_delete=models.CASCADE)
    notification_mode = models.ManyToManyField(NotificationMode)
    notification_timing = models.ManyToManyField(NotificationTiming)

    class Meta:
        verbose_name = 'configuração'
        verbose_name_plural = 'configurações'
    
    def __repr__(self):
        return self.user.username if self.user else 'Todos'

    def __str__(self):
        return self.user.username if self.user else 'Todos'

class Essay(models.Model):
    student_name = models.CharField(verbose_name='aluno', max_length=256)
    student_email = models.CharField(verbose_name='email', max_length=256, null=True, blank=True)
    monitor = models.ForeignKey(User, verbose_name='monitor', null=True, blank=True, on_delete=models.CASCADE)
    grade_1 = models.IntegerField(verbose_name='competência 1', default=0)
    grade_2 = models.IntegerField(verbose_name='competência 2', default=0)
    grade_3 = models.IntegerField(verbose_name='competência 3', default=0)
    grade_4 = models.IntegerField(verbose_name='competência 4', default=0)
    grade_5 = models.IntegerField(verbose_name='competência 5', default=0)
    final_grade = models.IntegerField(verbose_name='nota final', editable=False, default=0)
    created = models.DateTimeField(editable=False)
    last_modified = models.DateTimeField(editable=False, verbose_name='última modificação')
    essay_unredacted = models.FileField(verbose_name='redação', upload_to='essay/uploads', null=True, blank=True) 
    essay_redacted = models.FileField(verbose_name='redação corrigida', upload_to='essay/uploads', null=True, blank=True)
    has_essay = models.BooleanField(editable=False, default=False)
    has_correction = models.BooleanField(editable=False, default=False, verbose_name='corrigida')
    has_monitor = models.BooleanField(editable=False, default=False)
    notified = models.BooleanField(editable=False, default=False)

    class Meta:
        ordering = ('last_modified', 'has_essay', 'has_correction')
        verbose_name = 'redação'
        verbose_name_plural = 'redações'

    def _pushed_notify(self, content):
        if not content:
            return

        payload = {
            'app_key': 'BuOsbbNilU2hbuykX9Mq',
            'app_secret': 'NTq1qC7giKAUEnDK6RLz0gCuVDxOYHoZDtCp7mX314YseFomkYo6gg6s9BReXfv4',
            'target_type': 'app',
            'content': content
        }
        requests.post('https://api.pushed.co/1/push', data=payload)

    def save(self, *args, **kwargs):
        # TODO: send redacted essay to students email 

        content = None
        self.last_modified = timezone.now()
        
        if self.essay_unredacted:
            if not self.has_essay:
                self.has_essay = True
                content = 'Nova redação no sistema! Aluno: {}'.format(self.student_name)
                for config in NotificationConfiguration.objects.filter(notification_mode__id='MODE_MAIL', notification_timing__id='ON_ESSAY_UPLOAD'):
                    if not config.user or not config.user.email: continue
                    _start_new_thread(_email_notify, (content, config.user.email, self.student_name) )
                for config in NotificationConfiguration.objects.filter(notification_mode__id='MODE_PUSHED', notification_timing__id='ON_ESSAY_UPLOAD'):
                    if not config.user or not config.user.email: continue
                    self._pushed_notify(content)
        else:
            self.has_essay = False

        if not self.id:
            self.created = timezone.now()
                
        if self.monitor:
            if not self.has_monitor:
                self.has_monitor = True
                content = 'Nova redação a corrigir! Aluno: {}'.format(self.student_name)
                _start_new_thread(_email_notify, (content, self.monitor.email, self.student_name) )

        if self.essay_redacted:
            self.has_correction = True
            if not self.notified:
                self.notified = True
                content = 'Redação corrigida! Aluno: {}'.format(self.student_name)
                for config in NotificationConfiguration.objects.filter(notification_mode__id='MODE_MAIL', notification_timing__id='ON_ESSAY_REDACTED'):
                    if not config.user or not config.user.email: continue
                    _start_new_thread(_email_notify, (content, config.user.email, self.student_name) )
                for config in NotificationConfiguration.objects.filter(notification_mode__id='MODE_PUSHED', notification_timing__id='ON_ESSAY_REDACTED'):
                    if not config.user or not config.user.email: continue
                    self._pushed_notify(content)
        else:
            self.has_correction = False
            self.notified = False

        super().save(*args, **kwargs) 

    def __repr__(self):
        return self.student_name

    def __str__(self):
        return self.student_name
