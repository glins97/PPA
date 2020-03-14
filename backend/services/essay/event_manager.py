from .notification_manager import send_mail
def on_essay_upload(*args, **kwargs):
    from .models import NotificationConfiguration
    essay = args[0]
    fn = str(essay.file)
    if 'file' in kwargs:
        fn = str(kwargs['file'])
    if not fn: return
    for config in NotificationConfiguration.objects.all().filter(mode='MODE_MAIL', event='ON_ESSAY_UPLOAD'):
        send_mail(config.user.email, "Nova redação a ser corrigida!", "", fn)

def on_monitor_assignment(*args, **kwargs):    
    from .models import NotificationConfiguration
    essay = args[0]
    fn = str(essay.file)
    if 'file' in kwargs:
        fn = str(kwargs['file'])
    if not fn: return
    for config in NotificationConfiguration.objects.all().filter(mode='MODE_MAIL', event='ON_MONITOR_ASSIGNMENT'):
        send_mail(config.user.email, "Nova redação a ser corrigida!", "", fn)

def on_single_correction_done(*args, **kwargs):
    from .models import NotificationConfiguration
    essay = args[0]
    fn = str(essay.file)
    if 'file' in kwargs:
        fn = str(kwargs['file'])
    if not fn: return
    for config in NotificationConfiguration.objects.all().filter(mode='MODE_MAIL', event='ON_SINGLE_CORRECTION_DONE'):
        send_mail(config.user.email, "Redação corrigida!", "", fn)

def on_all_corrections_done(*args, **kwargs):
    from .models import NotificationConfiguration
    essay = args[0]
    fn = str(essay.file)
    if 'file' in kwargs:
        fn = str(kwargs['file'])
    if not fn: return
    for config in NotificationConfiguration.objects.all().filter(mode='MODE_MAIL', event='ON_ALL_CORRECTIONS_DONE'):
        send_mail(config.user.email, "Correção completa!", "", fn)

def on_delivery_date_arrived(*args, **kwargs):
    from .models import NotificationConfiguration
    essay = args[0]
    fn = str(essay.file)
    if 'file' in kwargs:
        fn = str(kwargs['file'])
    if not fn: return
    for config in NotificationConfiguration.objects.all().filter(mode='MODE_MAIL', event='ON_DELIVERY_DATE_ARRIVED'):
        send_mail(config.user.email, "Data de entrega limite atingida!", "", fn)

class EventManager(object):
    events = {
        'ON_ESSAY_UPLOAD': [ on_essay_upload ],
        'ON_MONITOR_ASSIGNMENT': [ on_monitor_assignment ],
        'ON_SINGLE_CORRECTION_DONE': [ on_single_correction_done ], 
        'ON_ALL_CORRECTIONS_DONE': [ on_all_corrections_done ],
        'ON_DELIVERY_DATE_ARRIVED': [ on_delivery_date_arrived ],
    }

    descriptions = {
        'ON_ESSAY_UPLOAD': 'Upload de Redação',
        'ON_MONITOR_ASSIGNMENT': 'Determinação de Monitor',
        'ON_SINGLE_CORRECTION_DONE': 'Correção Completa',
        'ON_ALL_CORRECTIONS_DONE': 'Todas as Correções Completas',
        'ON_DELIVERY_DATE_ARRIVED': 'Data Final de Entrega Atingida',
    }

    @staticmethod
    def list_registered_event():
        for event in EventManager.events:
            yield event

    @staticmethod
    def register_event(event_name):
        if event_name not in EventManager.events:
            EventManager.events[event_name] = []

    @staticmethod
    def register_event_callback(event_name, callback):
        if event_name not in EventManager.events:
            EventManager.register_event(event_name)
        EventManager.events[event_name].append(callback)

    @staticmethod
    def dispatch_event(event_name, *args, **kwargs):
        for callback in EventManager.events[event_name]:
            callback(*args, **kwargs)
