import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "services.settings")
django.setup()
from tps.auxilliary import name_format
from tps.models import Report
import pickle

reports = Report.objects.all().filter(correct_answer_1='')
answers = {}
with open('answers', 'rb') as handle:
    answers = pickle.load(handle)

for report in reports:
    if answers.get(report.name, None):
        print(report.name)
        for i in range(1, 11):
            setattr(report, 'correct_answer_' + str (i), answers[report.name]['correct_answer_' + str (i)])
        report.save()        