from django.db import models
from ..event_manager import EventManager
from django.contrib.auth.models import User 

notification_modes = [
    ('MODE_MAIL', 'Email'),
]

events = [
    ('ON_ESSAY_UPLOAD', 'Upload de Redação'),
    ('ON_MONITOR_ASSIGNMENT', 'Determinação de Monitor'),
    ('ON_SINGLE_CORRECTION_DONE', 'Correção Completa'),
    ('ON_ALL_CORRECTIONS_DONE', 'Todas as Correções Completas'),
    ('ON_DELIVERY_DATE_ARRIVED', 'Data Final de Entrega Atingida'),
]

for event_code, event_name in events:
    EventManager.register_event(event_code)

class NotificationConfiguration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mode = models.CharField(verbose_name='plataforma', choices=notification_modes, max_length=32)
    event = models.CharField(verbose_name='evento', choices=events, max_length=32)
    
    class Meta:
        verbose_name = 'notificação'
        verbose_name_plural = 'notificações'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{}: {} | {}'.format(self.user, self.mode, self.event)
