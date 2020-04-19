from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User 
from .student import Student
import subprocess
from datetime import timedelta

def essays_upload_to(essay, a):
    file_format = a[-3:]
    return 'uploads/essays/{}-{}-{}.{}'.format(essay.student.name, essay.student.school, essay.upload_date, file_format)

class Essay(models.Model):
    mail_id = models.CharField(default='', max_length=256, editable=False)
    student = models.ForeignKey(Student, verbose_name='Aluno', on_delete=models.CASCADE)
    file = models.FileField(verbose_name='redação', upload_to=essays_upload_to)
    redactions = models.ManyToManyField('Redaction', related_name='redactions', verbose_name='correções', null=True, blank=True)
    last_redaction = models.ForeignKey('Redaction', related_name='last_redaction', editable=False, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(editable=False, max_length=255, default='AGUARDANDO CORREÇÃO')
    
    upload_date = models.DateField(verbose_name='data de submissão', blank=True, null=True)
    last_modified = models.DateTimeField(verbose_name='última modificação', blank=True, null=True)
    delivery_date = models.DateField(verbose_name='data de entrega', blank=True, null=True)
    final_grade = models.IntegerField(verbose_name='nota final', default=0)
    
    has_essay = models.BooleanField(editable=False, default=False, verbose_name='possui redação')
    has_correction = models.BooleanField(default=False, verbose_name='correção finalizada')
    sent = models.BooleanField(default=False, verbose_name='enviado')
    max_redactions = models.IntegerField(editable=False, default=2)
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
            self.delivery_date = self.last_modified + timedelta(days=7)
        if self.has_correction:
            self.status = 'CORREÇÃO FINALIZADA'
        
        super().save(*args, **kwargs)

        # if new file is manually added, then append correction page
        if str(self.previous_file) != str(self.file):
            file_dir = str(self.file)
            print('FILE:', file_dir)
            if '.png' in file_dir.lower() or '.jpg' in file_dir.lower() or '.peg' in file_dir.lower():
                subprocess.call(['convert', file_dir, file_dir[:-4] + '.pdf'])
                file_dir = file_dir[:-4] + '.pdf'

            output = file_dir.replace('.pdf', '_.pdf')
            subprocess.call(['pdftk', file_dir, 'essay/inputs/MODEL.pdf', 'cat',  'output', output])
            self.file = output
        self.previous_file = self.file

        if not self.has_essay:
            self.has_essay = True

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