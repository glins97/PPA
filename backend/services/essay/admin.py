from django.contrib import admin
from django.urls import include, path, re_path
from django.http import HttpResponse, HttpResponseRedirect, Http404, FileResponse
from .models import NotificationMode, NotificationTiming, NotificationConfiguration, Essay 

class EssayAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'last_modified', 'has_correction', 'final_grade')
    list_filter = ('last_modified', 'has_correction', 'final_grade')
    search_fields = ('student_name', )
    list_per_page = 20

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            # re_path(r'(?P<fn>.*)', self.download),
            re_path(r'.+(?P<dir>essay/uploads/)(?P<fn>.+)/$', self.download),
        ]
        return my_urls + urls

    def download(self, request, dir, fn):
        return FileResponse(open(dir + fn, 'rb'), as_attachment=True, filename=fn)

class NotificationConfigurationAdmin(admin.ModelAdmin):
    list_display = ('user', 'plataforma', 'quando')
    list_per_page = 20

    def plataforma(self, obj):
        return ', '.join([mode.name for mode in obj.notification_mode.all()])

    def quando(self, obj):
        return ', '.join([timing.name for timing in obj.notification_timing.all()])

admin.site.register(NotificationMode)
admin.site.register(NotificationTiming)
admin.site.register(NotificationConfiguration, NotificationConfigurationAdmin)
admin.site.register(Essay, EssayAdmin)
