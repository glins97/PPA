from django.db import models
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
    class Meta:
        ordering = ('name',)
        verbose_name = 'relatório'
        verbose_name_plural = 'relatórios'
    
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name