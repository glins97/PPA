from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from .models import Student, Essay, Redaction
from django.utils.html import format_html
from .notification_manager import send_mail
from django.contrib import messages
from zipfile import ZipFile
from django import forms

class EssayAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('student', 'file', 'has_correction'),
        }),
        ('Dados', {
            'fields': ('redactions', 'final_grade', 'upload_date', 'last_modified', 'delivery_date', 'sent'),
        }),
    )
    autocomplete_fields = ('student', )
    list_filter = ('student__school', 'status', 'upload_date', 'final_grade', 'sent')
    search_fields = ('student__name', )
    readonly_fields = ('status', 'redactions', 'upload_date', 'delivery_date', 'last_modified', 'final_grade')
    list_per_page = 100

    def changelist_view(self, request, extra_context=None):
         if request.user.is_superuser:
             self.list_display = ('student', 'status', 'correção_1', 'correção_2', 'final_grade', 'arquivo', 'ação', 'email')
         else:
             self.list_display = ('student', 'status', 'correção_1', 'correção_2', 'final_grade', 'arquivo', 'ação')
         return super(EssayAdmin, self).changelist_view(request, extra_context)
    
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
                '<a class="button" href="change_status/{}/{}">INICIAR CORREÇÃO</a>&nbsp'.format(request.pk, 'CORRIGINDO'))
        
        return html

    def email(self, request):
        html = format_html('')
        if request.has_correction and not request.sent:
            if request.student.email:
                html += format_html(
                    '<a class="button" href="send/{}" style="background-color:#ff6960">ENVIAR CORREÇÃO</a>&nbsp'.format(request.pk))
            else:
                html += format_html(
                    '<a style="color:#ff6960">SEM EMAIL CADASTRADO</a>&nbsp')
        return html

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if request.path == '/admin/essay_probono/essay/autocomplete/':
            queryset = queryset.exclude(sent=True).exclude(has_correction=True)
        return queryset, use_distinct
    
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'school', 'email', 'number_of_essays', 'average_grade')
    search_fields = ('name', 'school', 'email')
    list_filter = ('school', 'number_of_essays')
    readonly_fields = ('number_of_essays', 'average_grade')

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
    list_display = ('essay', 'date', 'monitor', 'grades_average')
    list_filter = ('monitor', 'grades_average')
    # readonly_fields = ('grade_1', 'grade_2', 'grade_3', 'grade_4', 'grade_5')
    list_per_page = 100

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
admin.site.register(Redaction, RedactionAdmin)