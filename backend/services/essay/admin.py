from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from .models import School, Student, Essay, Redaction, NotificationConfiguration
from django.utils.html import format_html
from .notification_manager import send_mail
from django.contrib import messages
from zipfile import ZipFile
from django import forms

class EssayAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('student', 'file'),
        }),
        ('Monitores', {
            'fields': ('monitor_1', 'monitor_2', 'has_correction'),
        }),
        ('Dados', {
            'fields': ('redactions', 'final_grade', 'upload_date', 'last_modified', 'delivery_date', 'sent'),
        }),
    )
    autocomplete_fields = ('student', 'monitor_1', 'monitor_2')
    list_display = ('student', 'upload_date', 'last_modified', 'has_correction', 'monitor_1', 'monitor_2', 'final_grade', 'arquivo', 'sent', 'ação')
    list_filter = ('last_modified', 'has_correction', 'final_grade', 'sent', 'monitor_1', 'monitor_2')
    search_fields = ('student', )
    readonly_fields = ('sent', 'redactions', 'upload_date', 'delivery_date', 'last_modified', 'final_grade')
    list_per_page = 20

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'.+(?P<dir>uploads/essays/)(?P<fn>.+)/$', self.download),
            re_path(r'.+(?P<dir>uploads/redactions/)(?P<fn>.+)/$', self.download),
            re_path(r'.+(uploads/latest/)(?P<pk>.+)/$', self.latest),
            re_path(r'send/(?P<id>.+)/$', self.send),
        ]
        return my_urls + urls

    def download(self, request, dir, fn):
        return FileResponse(open(dir + fn, 'rb'), as_attachment=True, filename=fn)

    def latest(self, request, pk):
        return HttpResponseRedirect('../../../{url}'.format(url=Essay.objects.get(pk=pk).file.name))

    def arquivo(self, request):
        return format_html('<a href="view/uploads/latest/{pk}">Download</a>&nbsp'.format(pk=request.pk))
    
    def send(self, request, id):
        # TODO: JOIN PDFS, SEND IT
        try:            
            obj = Essay.objects.get(pk=id)
            sent = send_mail(obj.student.email, 'Redação corrigida!', '', str(obj.last_redaction.file))
            obj.sent = sent
            obj.save()
            if sent:
                self.message_user(request, "Correção enviada!")
            else:
                self.message_user(request, "Falha ao enviar correção, consulte o Administrador!", level=messages.ERROR)
        except Exception as e:
            print(e)
            self.message_user(request, "Falha ao enviar correção, consulte o Administrador!", level=messages.ERROR)
        return HttpResponseRedirect(r'../../')

    def ação(self, request):
        if request.student.school.send_mode_target == 'MODE_STUDENT' and request.has_correction:
            return format_html(
                '<a class="button" href="send/{}">ENVIAR CORREÇÃO</a>&nbsp'.format(request.pk))
        return format_html('')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'email', 'year', 'class_id', 'number_of_essays', 'average_grade')
    list_filter = ('school', 'year', 'number_of_essays')
    search_fields = ('name', 'school')
    readonly_fields = ('number_of_essays', 'average_grade')

class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'state', 'send_mode_target', 'ação')
    list_filter = ('state', 'city')
    search_fields = ('name', 'state')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'send/(?P<id>\d+)/$', self.send),
        ]
        return my_urls + urls

    def send(self, request, id):
        # TODO: JOIN PDFS, SEND IT
        # return FileResponse(open('uploads/redactions/' + fn, 'rb'), as_attachment=True, filename=fn)
        try:
            school = School.objects.get(pk=id)
            redactions = Redaction.objects.all().filter(essay__student__school__pk=school.pk, essay__sent=False)
            essays = [redaction.essay for redaction in redactions]
            if not redactions:
                self.message_user(request, "Não existem correções a enviar!")
            filenames = [str(redaction.file) for redaction in redactions]
            
            attachment = ZipFile('uploads/redactions/attachment-{}.zip'.format(school.name), 'w')
            for fn in filenames:
                if not fn: continue
                attachment.write(str(fn))
            attachment.close()

            sent = send_mail(school.email, 'Redação corrigida!', '', 'uploads/redactions/attachment-{}.zip'.format(school.name))
            for essay in essays: 
                essay.sent = sent
                essay.save()
            if sent:
                self.message_user(request, "Correções enviadas!")
            else:
                self.message_user(request, "Falha ao enviar correções, consulte o Administrador!", level=messages.ERROR)
        except Exception as e:
            print('Error @send ->', e)
            self.message_user(request, "Falha ao enviar correções, consulte o Administrador!", level=messages.ERROR)
        return HttpResponseRedirect(r'../../')

    def ação(self, request):
        if request.send_mode_target == 'MODE_SCHOOL':
            return format_html(
                '<a class="button" href="send/{}/">ENVIAR CORREÇÕES</a>&nbsp'.format(request.pk))
        return format_html('')

class RedactionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('essay', 'monitor', 'file'),
        }),
        ('Correção', {
            'fields': ('grade_1', 'grade_2', 'grade_3', 'grade_4', 'grade_5'),
        })
    )
    autocomplete_fields = ('essay', 'monitor')

    list_display = ('essay', 'monitor', 'date', 'grades_average')
    list_filter = ('monitor', 'grades_average')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'.+(?P<dir>uploads/redactions/)(?P<fn>.+)/$', self.download),
        ]
        return my_urls + urls

    def download(self, request, dir, fn):
        return FileResponse(open(dir + fn, 'rb'), as_attachment=True, filename=fn)

admin.site.register(Essay, EssayAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Redaction, RedactionAdmin)
admin.site.register(NotificationConfiguration)
