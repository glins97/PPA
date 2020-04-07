from django.db import models
from .school import School

class Student(models.Model):
    school = models.ForeignKey(School, verbose_name='campus', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='nome', max_length=256)
    email = models.CharField(verbose_name='email', max_length=256)
    identification = models.CharField(verbose_name='matrícula', max_length=32)
    year = models.CharField(verbose_name='ano', max_length=2)
    class_id = models.CharField(verbose_name='turma', max_length=256)
    number_of_essays = models.IntegerField(verbose_name='número de redações', default=0)
    average_grade = models.IntegerField(verbose_name='nota média', default=0)
    
    class Meta:
        verbose_name = 'aluno'
        verbose_name_plural = 'alunos'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name


