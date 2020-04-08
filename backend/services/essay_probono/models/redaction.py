from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from .essay import Essay
import PyPDF2

def redactions_upload_to(redaction, a):
    return 'uploads/redactions/[CORRECAO]-{}-{}-{}.pdf'.format(redaction.essay.student.name, redaction.essay.student.school, redaction.essay.upload_date)

class Redaction(models.Model):
    essay = models.ForeignKey(Essay, verbose_name='redação', on_delete=models.CASCADE)
    monitor = models.ForeignKey(User, related_name='probono_monitor', on_delete=models.CASCADE)
    grade_1 = models.IntegerField(verbose_name='competência 1', default=0)
    grade_2 = models.IntegerField(verbose_name='competência 2', default=0)
    grade_3 = models.IntegerField(verbose_name='competência 3', default=0)
    grade_4 = models.IntegerField(verbose_name='competência 4', default=0)
    grade_5 = models.IntegerField(verbose_name='competência 5', default=0)
    grades_average = models.IntegerField(verbose_name='nota', default=0, editable=False)
    date = models.DateTimeField(verbose_name='data de correção', blank=True, null=True, editable=False)
    file = models.FileField(verbose_name='correção', upload_to=redactions_upload_to, blank=True, null=True)

    class Meta:
        ordering = ('essay__student__name',)
        verbose_name = 'correção'
        verbose_name_plural = 'correções'

    def save(self, *args, **kwargs):
        self.essay.last_modified = timezone.now()
        self.date = timezone.now()
        g1, g2, g3, g4, g5 = 0, 0, 0, 0, 0
        super().save(*args, **kwargs) 
        if self.file:
            ff = None
            try:
                f = PyPDF2.PdfFileReader(self.file)
                ff = f.getFields()
                if ff: 
                    if ff['a1']['/V'] and not ff['b1']['/V']:
                        self.grade_1 = int(ff['a1']['/V'])
                    elif ff['a1']['/V'] and  ff['b1']['/V']:
                        self.grade_1 = int(ff['b1']['/V'])
                    else:
                        self.grade_1 = 0

                    if ff['a2']['/V'] and not ff['b2']['/V']:
                        self.grade_2 = int(ff['a2']['/V'])
                    elif ff['a2']['/V'] and  ff['b2']['/V']:
                        self.grade_2 = int(ff['b2']['/V'])
                    else:
                        self.grade_2 = 0

                    if ff['a3']['/V'] and not ff['b3']['/V']:
                        self.grade_3 = int(ff['a3']['/V'])
                    elif ff['a3']['/V'] and  ff['b3']['/V']:
                        self.grade_3 = int(ff['b3']['/V'])
                    else:
                        self.grade_3 = 0

                    if ff['a4']['/V'] and not ff['b4']['/V']:
                        self.grade_4 = int(ff['a4']['/V'])
                    elif ff['a4']['/V'] and  ff['b4']['/V']:
                        self.grade_4 = int(ff['b4']['/V'])
                    else:
                        self.grade_4 = 0

                    if ff['a5']['/V'] and not ff['b5']['/V']:
                        self.grade_5 = int(ff['a5']['/V'])
                    elif ff['a5']['/V'] and  ff['b5']['/V']:
                        self.grade_5 = int(ff['b5']['/V'])
                    else:
                        self.grade_5 = 0
            except Exception as e:
                self.message_user(request, "Falha ao ler PDF, por favor contate o Administrador!", level=messages.ERROR)
                print(repr(e))
            
        self.grades_average = 0
        self.grades_average += self.grade_1
        self.grades_average += self.grade_2
        self.grades_average += self.grade_3
        self.grades_average += self.grade_4
        self.grades_average += self.grade_5
        super().save(*args, **kwargs) 
        self.essay.add_redaction(self)


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{}: {}'.format(self.monitor, self.grades_average)

