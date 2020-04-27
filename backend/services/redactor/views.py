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
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.generic import BooleanObject, NameObject, IndirectObject, TextStringObject

def add_redaction_model(source, destination):
    subprocess.call(['pdftk', source, 'essay/inputs/MODEL.pdf', 'cat',  'output', destination])

def set_need_appearances_writer(writer):
    try:
        catalog = writer._root_object
        # get the AcroForm tree and add "/NeedAppearances attribute
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)
        return writer

    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))
        return writer

class PdfFileFiller(object):
    def __init__(self, infile):
        self.pdf = PdfFileReader(open(infile, "rb"), strict=False)
        if "/AcroForm" in self.pdf.trailer["/Root"]:
            self.pdf.trailer["/Root"]["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})
            
    def update_form_values(self, outfile, newvals={}, newchecks={}):
        self.pdf2 = MyPdfFileWriter()
        trailer = self.pdf.trailer["/Root"]["/AcroForm"]
        self.pdf2._root_object.update({
            NameObject('/AcroForm'): trailer})

        set_need_appearances_writer(self.pdf2)
        if "/AcroForm" in self.pdf2._root_object:
            self.pdf2._root_object["/AcroForm"].update(
            {NameObject("/NeedAppearances"): BooleanObject(True)})
        
        for i in range(self.pdf.getNumPages()):
            self.pdf2.addPage(self.pdf.getPage(i))
            self.pdf2.updatePageFormFieldValues(self.pdf2.getPage(i), newvals)
            self.pdf2.updatePageFormCheckboxValues(self.pdf2.getPage(i), newchecks)

        with open(outfile, 'wb') as out:
            self.pdf2.write(out)

class MyPdfFileWriter(PdfFileWriter):
    def __init__(self):
        super().__init__()
    def updatePageFormCheckboxValues(self, page, fields):

        for j in range(0, len(page['/Annots'])):
            writer_annot = page['/Annots'][j].getObject()
            for field in fields:
                if writer_annot.get('/T') == field:
                    writer_annot.update({
                        NameObject("/V"): NameObject(fields[field]),
                        NameObject("/AS"): NameObject(fields[field])
                    })

def fill_redaction_model(source, destination, values):
    c = PdfFileFiller(source)
    c. update_form_values(outfile=destination,
                          newvals=values)

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
        print('data', data)
        temp = 'redactor/temp/{}.pdf'.format(time.time())
        Document(data['source']).export(temp, data)
        temp2 = 'redactor/temp/{}.pdf'.format(time.time())
        add_redaction_model(temp, temp2)
        dest = data['destination'] + 'CORRECAO_' + get_fn(data['source']).replace('.jpg', '.pdf')
        fill_redaction_model(temp2, dest, data['competencies'])
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