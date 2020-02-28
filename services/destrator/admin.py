from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.utils.html import format_html
from django.conf import settings

from threading import Thread
from .models import TPS
from .auxilliary import name_format, download_csv_file, convert, retrieve_drive_files
import os 
import io
import pandas
import datetime

class TPSAdmin(admin.ModelAdmin):
    change_list_template = "change_list.html"
    list_display = ('name', 'url', 'last_modified', 'answers', 'action')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('update/', self.update),
            path('view/', self.view),
            re_path(r'^download_xlsx/(?P<id>[\w-]+)/$', self.download_xlsx),
            re_path(r'^download_pdf/(?P<id>[\w-]+)/$', self.download_pdf),
            re_path(r'^update_tps/(?P<id>[\w-]+)/$', self.update_tps),
        ]
        return my_urls + urls

    def action(self, request):
        return format_html(
            '<a class="button" href="download_xlsx/{}">XLSX</a>&nbsp'.format(request.id) +
            '<a class="button" href="download_pdf/{}">PDF</a>&nbsp'.format(request.id) +
            '<a class="button" href="update_tps/{}">UPDATE</a>'.format(request.id))
 
    def update(self, request):
        for f in retrieve_drive_files():
            tps = None
            data = download_csv_file(f['id'])[1]
            csv = pandas.read_csv(data)
            if TPS.objects.filter(id=f['id']).count():
                tps = TPS.objects.get(id=f['id'])
                if tps.answers < csv.shape[0] - 1:
                    tps.last_modified = datetime.datetime.now()
                tps.data = data.getvalue()
            else:
                tps = TPS.objects.create(
                    id=f['id'],
                    name=name_format(f['title']),
                    url=f['alternateLink'],
                    last_modified=datetime.datetime.now(),
                    answers=csv.shape[0] - 1,
                    data=data.getvalue(),
                )
            tps.save()
        self.message_user(request, "TPS atualizados!")
        return HttpResponseRedirect("../")

    def view(self, request):
        self.message_user(request, "View called!")
        return HttpResponseRedirect("../")

    def update_tps(self, request, id):
        tps = None
        id = str(id)
        data = download_csv_file(id)[1]
        csv = pandas.read_csv(data)
        if TPS.objects.filter(id=id).count():
            tps = TPS.objects.get(id=id)
            if tps.answers < csv.shape[0] - 1:
                tps.last_modified = datetime.datetime.now()
            tps.data = data.getvalue()
            tps.save()
        self.message_user(request, "TPS atualizado!")
        return HttpResponseRedirect("../../")

    def download_xlsx(self, request, id):
        tps = TPS.objects.get(id=id)
        fn, fdata = name_format(tps.name), io.BytesIO(tps.data)
        if '.xlsx' not in fn:
            fn += '.xlsx'  
        output = convert(fn, fdata)
        return FileResponse(open(output, 'rb'), as_attachment=True, filename=fn)

    def download_pdf(self, request, id):
        tps = TPS.objects.get(id=id)
        fn, fdata = name_format(tps.name), io.BytesIO(tps.data)
        if '.xlsx' not in fn:
            fn += '.xlsx'  
        output = convert(fn, fdata)
        os.system('libreoffice --headless --convert-to pdf "{}" --outdir destrator/outputs/'.format(output))
        return FileResponse(open(output.replace('.xlsx', '.pdf'), 'rb'), as_attachment=True, filename=fn.replace('.xlsx', '.pdf'))

admin.site.register(TPS, TPSAdmin)
