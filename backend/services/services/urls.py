from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

admin.site.site_header = "PPA Digital"
admin.site.site_title = "PPA Digital"
admin.site.index_title = "Bem vindo ao PPA Digital"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.ESSAYS_STATIC_URL, document_root=settings.ESSAYS_STATIC_URL)