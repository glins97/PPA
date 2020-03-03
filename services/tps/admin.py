from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.utils.html import format_html
from django.conf import settings

from threading import Thread
from .models import Report
from .auxilliary import name_format, download_csv_file, generate_distrator, generate_score_z, generate_tbl, retrieve_drive_files
import os 
import io
import pandas
import datetime

class ReportAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_modified', 'answers', 'download')

    list_filter = ('discipline', 'week', 'local', )
    search_fields = ('name', )
    list_per_page = 20

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'^download_pdf_score_z/(?P<id>[\w-]+)/$', self.download_pdf_score_z),
            re_path(r'^download_pdf_tbl/(?P<id>[\w-]+)/$', self.download_pdf_tbl),
            re_path(r'^download_pdf_distrator/(?P<id>[\w-]+)/$', self.download_pdf_distrator),
            re_path(r'^update_report/(?P<id>[\w-]+)/$', self.update_report),
        ]
        return my_urls + urls

    def download(self, request):
        return format_html(
            '<a class="button" href="download_pdf_score_z/{}">Score Z</a>&nbsp'.format(request.id) +
            '<a class="button" href="download_pdf_tbl/{}">TBL</a>&nbsp'.format(request.id) +
            '<a class="button" href="download_pdf_distrator/{}">Distrator</a>&nbsp'.format(request.id))

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
 
    def update(self, request):
        files = retrieve_drive_files()
        for f in files:
            report = None
            data = download_csv_file(f['id'], files)[1]
            csv = pandas.read_csv(data)
            if Report.objects.filter(id=f['id']).count():
                report = Report.objects.get(id=f['id'])
                if report.answers < csv.shape[0]:
                    report.last_modified = datetime.datetime.now()
                report.answers = csv.shape[0]
                report.data = data.getvalue()
                report.local = self.get_local(f['title'])
                report.week = self.get_week(f['title'])
                report.discipline = self.get_discipline(f['title']) 
            else:
                report = Report.objects.create(
                    id=f['id'],
                    name=name_format(f['title']),
                    url=f['alternateLink'],
                    last_modified=datetime.datetime.now(),
                    answers=csv.shape[0],
                    data=data.getvalue(),
                    local=self.get_local(f['title']),
                    week=self.get_week(f['title']),
                    discipline=self.get_discipline(f['title']),
                )
            report.save()
        self.message_user(request, "Report atualizados!")
        return HttpResponseRedirect("../")

    def update_report(self, request, id):
        report = None
        id = str(id)
        data = download_csv_file(id)[1]
        csv = pandas.read_csv(data)
        if Report.objects.filter(id=id).count():
            report = Report.objects.get(id=id)
            if report.answers < csv.shape[0]:
                report.last_modified = datetime.datetime.now()
            report.answers = csv.shape[0]
            report.data = data.getvalue()
            report.save()
        self.message_user(request, "Report atualizado!")
        return HttpResponseRedirect("../../")

    def download_xlsx(self, request, id):
        report = Report.objects.get(id=id)
        fn, fdata = name_format(report.name), io.BytesIO(report.data)
        if '.xlsx' not in fn:
            fn += '.xlsx'  
        output = convert(fn, fdata)
        return FileResponse(open(output, 'rb'), as_attachment=True, filename=fn)

    def _gen_pdf(self, id, func):
        report = Report.objects.get(id=id)
        fn, fdata = name_format(report.name), io.BytesIO(report.data)
        fn += ' ' + func.upper().replace('_', ' ') + '.pdf'
        output = None
        if func == 'score_z':
            output = generate_score_z(fn, fdata)
        if func == 'tbl':
            output = generate_tbl(fn, fdata)
        if func == 'distrator':
            output = generate_distrator(fn, fdata)

        os.system('libreoffice --headless --convert-to pdf "{}" --outdir tps/outputs/'.format(output))
        return FileResponse(open(output.replace('.xlsx', '.pdf'), 'rb'), as_attachment=True, filename=fn)

    def download_pdf_score_z(self, request, id):
        return self._gen_pdf(id, 'score_z')

    def download_pdf_tbl(self, request, id):
        return self._gen_pdf(id, 'tbl')

    def download_pdf_distrator(self, request, id):
        return self._gen_pdf(id, 'distrator')

admin.site.register(Report, ReportAdmin)
