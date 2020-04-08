from django.db import models

class Student(models.Model):
    name = models.CharField(verbose_name='nome', max_length=256)
    email = models.CharField(verbose_name='email', max_length=256)
    school = models.CharField(verbose_name='escola', max_length=256, null=True, blank=True, default='')
    number_of_essays = models.IntegerField(verbose_name='número de redações', default=0, editable=False)
    average_grade = models.IntegerField(verbose_name='nota média', default=0, editable=False)
    
    class Meta:
        verbose_name = 'aluno'
        verbose_name_plural = 'alunos'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


