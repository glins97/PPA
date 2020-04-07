from django.db import models

send_target_modes = [
    ('MODE_STUDENT', 'Estudante'),
    ('MODE_SCHOOL', 'Escola'),
]

class School(models.Model):
    name = models.CharField(verbose_name='nome', max_length=256)
    state = models.CharField(verbose_name='estado', max_length=2)
    city = models.CharField(verbose_name='cidade', max_length=32) 
    email = models.CharField(verbose_name='email', max_length=256)
    days_to_redact = models.IntegerField(verbose_name='dias de correção', default=7)
    send_mode_target = models.CharField(verbose_name='enviar correções para', choices=send_target_modes, max_length=32)
    
    class Meta:
        verbose_name = 'escola'
        verbose_name_plural = 'escolas'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return self.name