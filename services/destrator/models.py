from django.db import models
choices = (
    ('A', 'A'),
    ('B', 'B'),
    ('C', 'C'),
    ('D', 'D'),
    ('E', 'E'),
)

class TPS(models.Model):
    id = models.TextField(primary_key=True, editable=False)
    name = models.TextField()
    url = models.TextField()
    local = models.TextField()
    discipline = models.TextField()
    week = models.TextField()
    last_modified = models.DateField()
    answers = models.IntegerField()
    data = models.BinaryField()
    class Meta:
        verbose_name = 'TPS'
        verbose_name_plural = 'TPS'
    
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class TPSAnswer(models.Model):
    email = models.TextField()
    name = models.TextField()
    submission = models.DateField()
    grade = models.IntegerField()
    q1 = models.CharField(max_length=1, choices=choices)
    q2 = models.CharField(max_length=1, choices=choices)
    q3 = models.CharField(max_length=1, choices=choices)
    q4 = models.CharField(max_length=1, choices=choices)
    q5 = models.CharField(max_length=1, choices=choices)
    q6 = models.CharField(max_length=1, choices=choices)
    q7 = models.CharField(max_length=1, choices=choices)
    q8 = models.CharField(max_length=1, choices=choices)
    q9 = models.CharField(max_length=1, choices=choices)
    q10 = models.CharField(max_length=1, choices=choices)
