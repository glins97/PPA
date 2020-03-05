from django.db import models
from .auxilliary import *
choices = (
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
)

class Report(models.Model):
    id = models.TextField(primary_key=True, editable=False)
    name = models.TextField(verbose_name='nome')
    url = models.TextField()
    local = models.TextField(verbose_name='campus')
    discipline = models.TextField(verbose_name='disciplina')
    week = models.TextField(verbose_name='semana')
    last_modified = models.DateField(verbose_name='última modificação')
    answers = models.IntegerField(verbose_name='respostas')
    data = models.BinaryField()
    correct_answer_1 = models.CharField(verbose_name='gabarito questão 1', max_length=1, choices=choices, default='')
    correct_answer_2 = models.CharField(verbose_name='gabarito questão 2', max_length=1, choices=choices, default='')
    correct_answer_3 = models.CharField(verbose_name='gabarito questão 3', max_length=1, choices=choices, default='')
    correct_answer_4 = models.CharField(verbose_name='gabarito questão 4', max_length=1, choices=choices, default='')
    correct_answer_5 = models.CharField(verbose_name='gabarito questão 5', max_length=1, choices=choices, default='')
    correct_answer_6 = models.CharField(verbose_name='gabarito questão 6', max_length=1, choices=choices, default='')
    correct_answer_7 = models.CharField(verbose_name='gabarito questão 7', max_length=1, choices=choices, default='')
    correct_answer_8 = models.CharField(verbose_name='gabarito questão 8', max_length=1, choices=choices, default='')
    correct_answer_9 = models.CharField(verbose_name='gabarito questão 9', max_length=1, choices=choices, default='')
    correct_answer_10 = models.CharField(verbose_name='gabarito questão 10', max_length=1, choices=choices, default='')

    def update(self):
        print('@report.update')
        data = download_by_id(self.id)
        csv = pandas.read_csv(data)
        if self.answers < csv.shape[0]:
            self.last_modified = datetime.datetime.now()
        self.answers = csv.shape[0]
        self.data = data.getvalue()
        self.save()

    class Meta:
        ordering = ('name',)
        verbose_name = 'relatório'
        verbose_name_plural = 'relatórios'
    
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name