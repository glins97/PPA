from django.shortcuts import render
from django.conf import settings
from .document import Document
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from pdf2image import convert_from_path
import time
import subprocess

def add_redaction_model(source, destination):
    subprocess.call(['pdftk', source, 'essay/inputs/MODEL.pdf', 'cat',  'output', destination])

def csrf_exempt_on_debug(func):
    return csrf_exempt(func) if settings.DEBUG else func

def get_fn(source):
    return source.split('/')[-1]

def get_extension(source):
    return get_fn(source).split('.')[-1]

@csrf_exempt_on_debug
def api_generate_document(request):
    response = HttpResponse()
    try:
        data = json.loads(request.body)
        temp = 'redactor/temp/{}.pdf'.format(time.time())
        dest = data['destination'] + 'CORRECAO_' + get_fn(data['source']).replace('.jpg', '.pdf')
        Document(data['source']).export(temp, data)
        add_redaction_model(temp, dest)
        response.write(dest)
        response.status_code = 200
    except Exception as e:
        logging.error(repr(e))
        response.write(repr(e))
        response.status_code = 500
    return response

@csrf_exempt_on_debug
def extract_first_page(request):
    try:
        data = json.loads(request.body)
        convert_from_path(data['source'], 1)[0].save(data['destination'], 'JPEG')
        if data:
            return HttpResponse()
        else:
            return HttpResponseForbidden()
    except:
        return HttpResponseForbidden()

@csrf_exempt_on_debug
def show(request):
    try:
        data = {}
        if request.body:
            data = json.loads(request.body)
        else:
            data = dict(request.GET)
            data['source'] = data['source'][0]
            data['destination'] = data['destination'][0]
            data['outbound_url'] = data['outbound_url'][0]

        if get_extension(data['source']) == 'pdf':
            source = 'redactor/temp/' + get_fn(data['source']).replace('.PDF', 'jpg').replace('.pdf', '.jpg')
            convert_from_path(data['source'])[0].save(source, 'JPEG')
            data['source'] = source

        data['source'] = data['source'].replace('redactor/', '')
        if data:
            return render(request, 'index.html', data)
        else:
            return HttpResponseForbidden()

    except Exception as e:
        logging.error('redactor::show@' + repr(e))
        return HttpResponseForbidden()