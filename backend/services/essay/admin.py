from django import forms
from django.contrib import admin, messages
from django.urls import include, path, re_path
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from django.utils.html import format_html
from django.contrib.messages import constants as messages

from .models import School, Student, Essay, Redaction, NotificationConfiguration
from .notification_manager import send_mail

from zipfile import ZipFile
class EssayAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('student', 'file', 'theme'),
        }),
        ('Monitores', {
            'fields': ('monitor_1', 'monitor_2', 'has_correction'),
        }),
        ('Dados', {
            'fields': ('redactions', 'final_grade', 'upload_date', 'last_modified', 'delivery_date', 'sent'),
        }),
    )
    autocomplete_fields = ('student', 'monitor_1', 'monitor_2')
    list_filter = ('student__school', 'student__class_id', 'status', 'theme', 'upload_date', 'final_grade', 'sent')
    search_fields = ('student__name', )
    readonly_fields = ('status', 'redactions', 'upload_date', 'delivery_date', 'last_modified', 'final_grade')
    list_per_page = 100

    def changelist_view(self, request, extra_context=None):
         if request.user.is_superuser:
             self.list_display = ('id', 'theme', 'student', 'status', 'correção_1', 'correção_2', 'final_grade', 'arquivo', 'ação', 'email')
         else:
             self.list_display = ('id', 'theme', 'student', 'status', 'correção_1', 'correção_2', 'final_grade', 'arquivo', 'ação')
         return super(EssayAdmin, self).changelist_view(request, extra_context)
    
    def id(self, essay):
        return essay.pk

    def correção_1(self, essay):
        redactions = essay.redactions.all()
        if len(redactions) > 0:
            return redactions[0].grades_average
        else:
            if essay.status == 'CORRIGINDO':
                return 'EM ANDAMENTO'
        return '-'

    def correção_2(self, essay):
        redactions = essay.redactions.all()
        if len(redactions) > 1:
            return redactions[1].grades_average
        else:
            if len(redactions) > 0:
                if essay.status == 'CORRIGINDO':
                    return 'EM ANDAMENTO'
        return '-'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'.+(?P<dir>uploads/essays/)(?P<fn>.+)/$', self.download),
            re_path(r'.+(?P<dir>uploads/redactions/)(?P<fn>.+)/$', self.download),
            re_path(r'.+(uploads/latest/)(?P<pk>.+)/$', self.latest),
            re_path(r'send/(?P<id>.+)/$', self.send),
            re_path(r'change_status/(?P<id>.+)/(?P<status>.+)/$', self.change_status),
        ]
        return my_urls + urls

    def download(self, request, dir, fn):
        return FileResponse(open(dir + fn, 'rb'), as_attachment=True, filename=fn)

    def latest(self, request, pk):
        return HttpResponseRedirect('../../../{url}'.format(url=Essay.objects.get(pk=pk).file.name))

    def arquivo(self, request):
        return format_html('<a href="view/uploads/latest/{pk}">DOWNLOAD</a>&nbsp'.format(pk=request.pk))
    
    def change_status(self, request, id, status):
        try:            
            obj = Essay.objects.get(pk=id)
            obj.status = status
            obj.save()
            self.message_user(request, "Status atualizado!")
            return HttpResponseRedirect(r'../../../../redaction/add/?essay=' + str(id))
        except Exception as e:
            print(e)
            self.message_user(request, "Falha ao atualizar status, consulte o Administrador!", level=messages.ERROR)
            return HttpResponseRedirect(r'../../../')

    def send(self, request, id):
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
        html = format_html('')
        if request.status == 'AGUARDANDO CORREÇÃO':
            html += format_html(
                '<a class="button" href="change_status/{}/{}">INICIAR CORREÇÃO</a>&nbsp'.format(request.pk, 'CORRIGINDO'))
        
        return html

    def email(self, request):
        html = format_html('')
        if request.student.school.send_mode_target == 'MODE_STUDENT' and request.has_correction and not request.sent:
            if request.student.email:
                html += format_html(
                    '<a class="button" href="send/{}" style="background-color:#ff6960">ENVIAR CORREÇÃO</a>&nbsp'.format(request.pk))
            else:
                html += format_html(
                    '<a style="color:#ff6960">SEM EMAIL CADASTRADO</a>&nbsp')
        return html

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if request.path == '/admin/essay/essay/autocomplete/':
            queryset = queryset.exclude(sent=True).exclude(has_correction=True)
        return queryset, use_distinct
    
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'class_id', 'email', 'number_of_essays', 'average_grade')
    list_filter = ('school', 'class_id', 'number_of_essays')
    search_fields = ('name', 'school__name', 'class_id')
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
                '<a class="button" href="send/{}/">ENVIAR CORREÇÕES</a>&nbsp'.format(request.pk))
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
    search_fields = ('essay__student__name',)
    list_display = ('essay', 'date', 'campus', 'turma', 'monitor', 'grades_average')
    list_filter = ('essay__student__school', 'essay__student__class_id', 'monitor', 'grades_average')
    readonly_fields = ('grade_1', 'grade_2', 'grade_3', 'grade_4', 'grade_5')
    list_per_page = 100

    def campus(self, redaction):
        if redaction and redaction.essay and redaction.essay.student and redaction.essay.student.school:
            return redaction.essay.student.school.name
        return ''

    def turma(self, redaction):
        if redaction and redaction.essay and redaction.essay.student and redaction.essay.student:
            return redaction.essay.student.class_id
        return ''

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            re_path(r'.+(?P<dir>uploads/redactions/)(?P<fn>.+)/$', self.download),
        ]
        return my_urls + urls

    def download(self, request, dir, fn):
        return FileResponse(open(dir + fn, 'rb'), as_attachment=True, filename=fn)

    def get_form(self, request, obj=None, **kwargs):
        print('request', request.GET, request.user)
        form = super(RedactionAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['monitor'].initial = None
        if request and request.user:
            form.base_fields['monitor'].initial = request.user
        if request and request.GET and 'essay' in request.GET:
            form.base_fields['essay'].initial = request.GET['essay']
        return form

admin.site.register(Essay, EssayAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(School, SchoolAdmin)
admin.site.register(Redaction, RedactionAdmin)
admin.site.register(NotificationConfiguration)
