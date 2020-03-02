import datetime
import os, django
import pandas
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "services.settings")
django.setup()

from destrator.models import TPS, TPSAnswer
from destrator.auxilliary import retrieve_drive_files, name_format, download_csv_file

def get_local(fn):
    return 'BRASÍLIA' if 'BRASÍLIA' in fn else 'JUAZEIRO'

def get_discipline(fn):
    discs = {
        'FÍS': ['FÍS', 'FIS'],
        'QUÍ': ['QUÍ', 'QUI'],
        'MAT': ['MAT'],
        'BIO': ['BIO'],
        }
    for disc in discs:
        for alias in discs[disc]:
            if alias in fn:
                return disc
    return '-'

def get_week(fn):
    weeks = ['SEM' + str(item) for item in range(1, 34)] + ['SEM ' + str(item) for item in range(1, 34)] 
    for week in weeks:
        if week in fn:
            return week
    return '-'

files = retrieve_drive_files()
for f in files:
    tps = None
    data = download_csv_file(f['id'], files)[1]
    csv = pandas.read_csv(data)
    if TPS.objects.filter(id=f['id']).count():
        tps = TPS.objects.get(id=f['id'])
        if tps.answers < csv.shape[0]:
            tps.last_modified = datetime.datetime.now()
        tps.answers = csv.shape[0]
        tps.data = data.getvalue()
        tps.local = local=get_local(f['title'])
        tps.week = get_week(f['title'])
        tps.discipline = get_discipline(f['title']) 
    else:
        tps = TPS.objects.create(
            id=f['id'],
            name=name_format(f['title']),
            url=f['alternateLink'],
            last_modified=datetime.datetime.now(),
            answers=csv.shape[0],
            data=data.getvalue(),
            local=get_local(f['title']),
            week=get_week(f['title']),
            discipline=get_discipline(f['title']),
        )
    tps.save()
