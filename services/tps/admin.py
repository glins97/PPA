from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.utils.html import format_html
from django.conf import settings

from threading import Thread
from .models import Report
from .auxilliary import *
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
        if request.user == 'glins':
            return True
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'^download_pdf_score_z/(?P<id>[\w-]+)/$', self.download_pdf_score_z),
            re_path(r'^download_pdf_tbl/(?P<id>[\w-]+)/$', self.download_pdf_tbl),
            re_path(r'^download_pdf_distrator/(?P<id>[\w-]+)/$', self.download_pdf_distrator),
        ]
        return my_urls + urls

    def download(self, request):
        return format_html(
            '<a class="button" href="download_pdf_score_z/{}">Score Z</a>&nbsp'.format(request.id) +
            '<a class="button" href="download_pdf_tbl/{}">TBL</a>&nbsp'.format(request.id) +
            '<a class="button" href="download_pdf_distrator/{}">Distrator</a>&nbsp'.format(request.id))

    def _gen_pdf(self, id, func):
        report = Report.objects.get(id=id)
        report.update()
        fn, fdata = name_format(report.name), io.BytesIO(report.data)
        fn += ' ' + func.upper().replace('_', ' ') + '.pdf'
        output = None
        if func == 'score_z':
            output = generate_score_z(fn, fdata)
        if func == 'tbl':
            output = generate_tbl(fn, fdata)
        if func == 'distrator':
            output = generate_distrator(fn, fdata, report)

        os.system('libreoffice --headless --convert-to pdf "{}" --outdir tps/outputs/'.format(output))
        return FileResponse(open(output.replace('.xlsx', '.pdf'), 'rb'), as_attachment=True, filename=fn)

    def download_pdf_score_z(self, request, id):
        return self._gen_pdf(id, 'score_z')

    def download_pdf_tbl(self, request, id):
        return self._gen_pdf(id, 'tbl')

    def download_pdf_distrator(self, request, id):
        return self._gen_pdf(id, 'distrator')

admin.site.register(Report, ReportAdmin)
