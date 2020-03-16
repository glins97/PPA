import datetime
import os, django
import pandas
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "services.settings")
django.setup()

from tps.models import Report
from tps.auxilliary import retrieve_drive_files, name_format, download_by_id

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
    report = None
    data = download_by_id(f['id'])
    csv = pandas.read_csv(data)
    if Report.objects.filter(id=f['id']).count():
        report = Report.objects.get(id=f['id'])
        if report.answers < csv.shape[0]:
            report.last_modified = datetime.datetime.now()
            print(' --> UPDATED')
        report.answers = csv.shape[0]
        report.data = data.getvalue()
    else:
        report = Report.objects.create(
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
    report.save()
