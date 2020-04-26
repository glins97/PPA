from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from redactor.views import show, api_generate_document, extract_first_page

admin.site.site_header = "PPA Digital"
admin.site.site_title = "PPA Digital"
admin.site.index_title = "Bem vindo ao PPA Digital"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', admin.site.urls),
    path('redactor/', show),
    path('api/v1/redactor/gen/', api_generate_document),
    path('api/v1/redactor/efp/', extract_first_page),
]

if settings.DEBUG:
    urlpatterns += static(settings.ESSAYS_STATIC_URL, document_root=settings.ESSAYS_STATIC_URL)
    urlpatterns += static('/uploads/essays_probono/', document_root=(settings.BASE_DIR + '/uploads/essays_probono/'))
    urlpatterns += static('/uploads/essays/', document_root=(settings.BASE_DIR + '/uploads/essays/'))
    urlpatterns += static('/redactor/images/', document_root=(settings.BASE_DIR + '/redactor/images/'))
    urlpatterns += static('/redactor/temp/', document_root=(settings.BASE_DIR + '/redactor/temp/'))
    