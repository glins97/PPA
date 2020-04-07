from django.db import models
from django.contrib.auth.models import User 
from django.utils import timezone
from .essay import Essay
from ..event_manager import EventManager

def redactions_upload_to(redaction, a):
    return 'uploads/redactions/[CORRECAO]-{}-{}-{}.pdf'.format(redaction.essay.student.name, redaction.essay.student.school.name, redaction.essay.upload_date)

class Redaction(models.Model):
    essay = models.ForeignKey(Essay, verbose_name='aluno', on_delete=models.CASCADE)
    monitor = models.ForeignKey(User, on_delete=models.CASCADE)
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
                        g1 = int(ff['a1']['/V'])
                    elif ff['a1']['/V'] and  ff['b1']['/V']:
                        g1 = int(ff['b1']['/V'])
                    else:
                        g1 = 0

                    if ff['a2']['/V'] and not ff['b2']['/V']:
                        g2 = int(ff['a2']['/V'])
                    elif ff['a2']['/V'] and  ff['b2']['/V']:
                        g2 = int(ff['b2']['/V'])
                    else:
                        g2 = 0

                    if ff['a3']['/V'] and not ff['b3']['/V']:
                        g3 = int(ff['a3']['/V'])
                    elif ff['a3']['/V'] and  ff['b3']['/V']:
                        g3 = int(ff['b3']['/V'])
                    else:
                        g3 = 0

                    if ff['a4']['/V'] and not ff['b4']['/V']:
                        g4 = int(ff['a4']['/V'])
                    elif ff['a4']['/V'] and  ff['b4']['/V']:
                        g4 = int(ff['b4']['/V'])
                    else:
                        g4 = 0

                    if ff['a5']['/V'] and not ff['b5']['/V']:
                        g5 = int(ff['a5']['/V'])
                    elif ff['a5']['/V'] and  ff['b5']['/V']:
                        g5 = int(ff['b5']['/V'])
                    else:
                        g5 = 0
            except:
                pass
                # print()
                # self.message_user(request, "Falha ao ler PDF, por favor contate o Administrador!", level=messages.ERROR)
            
        self.grades_average = 0
        self.grades_average += max([self.grade_1, g1])
        self.grades_average += max([self.grade_2, g2])
        self.grades_average += max([self.grade_3, g3])
        self.grades_average += max([self.grade_4, g4])
        self.grades_average += max([self.grade_5, g5])
        super().save(*args, **kwargs) 
        EventManager.dispatch_event('ON_SINGLE_CORRECTION_DONE', self.essay, file=self.file)
        self.essay.add_redaction(self)


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{}: {}'.format(self.monitor, self.grades_average)

