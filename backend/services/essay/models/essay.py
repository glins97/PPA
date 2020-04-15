from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User 
from .student import Student
from ..event_manager import EventManager
import subprocess
from datetime import timedelta

def essays_upload_to(essay, a):
    file_format = a[-3:]
    return 'uploads/essays/{}-{}-{}.{}'.format(essay.student.name, essay.student.school.name, essay.upload_date, file_format)

class Essay(models.Model):
    student = models.ForeignKey(Student, verbose_name='Aluno', on_delete=models.CASCADE)
    
    file = models.FileField(verbose_name='redação', upload_to=essays_upload_to)
    redactions = models.ManyToManyField('Redaction', related_name='redactions', verbose_name='correções', null=True, blank=True)
    last_redaction = models.ForeignKey('Redaction', related_name='last_redaction', editable=False, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(editable=False, max_length=255, default='AGUARDANDO CORREÇÃO')
    theme = models.CharField(verbose_name='Tema', max_length=255, null=True, blank=True)
    
    upload_date = models.DateField(verbose_name='data de submissão', blank=True, null=True)
    last_modified = models.DateTimeField(verbose_name='última modificação', blank=True, null=True)
    delivery_date = models.DateField(verbose_name='data de entrega', blank=True, null=True)
        
    monitor_1 = models.ForeignKey(User, related_name='monitor_1', on_delete=models.CASCADE, blank=True, null=True)
    monitor_2 = models.ForeignKey(User, related_name='monitor_2', on_delete=models.CASCADE, blank=True, null=True)
    final_grade = models.IntegerField(verbose_name='nota final', default=0)
    
    has_essay = models.BooleanField(editable=False, default=False, verbose_name='possui redação')
    has_correction = models.BooleanField(default=False, verbose_name='correção finalizada')
    sent = models.BooleanField(default=False, verbose_name='enviado')
    max_redactions = models.IntegerField(editable=False, default=2)
    has_monitor_1 = models.BooleanField(editable=False, default=False)
    has_monitor_2 = models.BooleanField(editable=False, default=False)
    previous_file = models.FileField(null=True, blank=True)

    class Meta:
        ordering = ('upload_date', 'last_modified', 'has_essay', '-has_correction', 'student__name')
        verbose_name = 'redação'
        verbose_name_plural = 'redações'

    def add_redaction(self, redaction):
        if redaction.file:
            self.file = redaction.file
            self.previous_file = redaction.file # prevent triage from triggering
        self.redactions.add(redaction)
        self.last_redaction = redaction
        self.final_grade = 0
        self.status = 'AGUARDANDO CORREÇÃO'
        for redaction in self.redactions.all():
            self.final_grade += redaction.grades_average
        self.final_grade = self.final_grade / len(self.redactions.all())
        
        if len(self.redactions.all()) >= self.max_redactions:
            self.has_correction = True
        
        self.save()
    
    def save(self, *args, **kwargs):
        self.last_modified = timezone.now()
        if not self.id:
            self.upload_date = self.last_modified
            self.delivery_date = self.last_modified + timedelta(days=self.student.school.days_to_redact)
        if self.has_correction:
            self.status = 'CORREÇÃO FINALIZADA'
        
        super().save(*args, **kwargs)

        # if new file is manually added, then append correction page
        if str(self.previous_file) != str(self.file):
            file_dir = str(self.file)
            print('TRIAGE START:', file_dir)
            if '.png' in file_dir.lower() or '.jpg' in file_dir.lower() or '.peg' in file_dir.lower():
                subprocess.call(['convert', file_dir, file_dir[:-4] + '.pdf'])
                file_dir = file_dir[:-4] + '.pdf'

            output = file_dir.replace('.pdf', '_.pdf')
            subprocess.call(['pdftk', file_dir, 'essay/inputs/MODEL.pdf', 'cat',  'output', output])
            self.file = output
            print('END OF TRIAGE')
        self.previous_file = self.file

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
        return '{} - {}'.format(self.student, self.theme if self.theme else self.pk)