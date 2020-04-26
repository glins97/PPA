from io import BytesIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen.canvas import Canvas
from PIL import Image

from PyPDF2.generic import (
    DictionaryObject,
    NumberObject,
    FloatObject,
    NameObject,
    TextStringObject,
    ArrayObject
)

class Document():
    def __init__(self, source):
        if 'redactor/' not in source:
            source = 'redactor/' + source 

        try:
            im = Image.open(source)
        except Exception as e:
            raise Exception('Failed to open image source ' + source)

        source = source.replace('/in/', '/temp/')
        self.page_size = 1240, int(1240.0 * im.size[1] / im.size[0])  
        im = im.resize(self.page_size, Image.ANTIALIAS)
        im.save(source)

        document = BytesIO()
        canvas = Canvas(document, pagesize=(self.page_size))  
        canvas.setFillColorRGB(1, 1, 1)
        canvas.drawImage(source, 0, 0, mask=(1, 1, 1, 1, 1, 1))
        canvas.save()
        self.pdf = PdfFileWriter()
        self.pdf.addPage(PdfFileReader(BytesIO(document.getvalue())).getPage(0))
        
    def add_line(self, x0, y0, x1, y1, color):
        document = BytesIO()
        canvas = Canvas(document, pagesize=self.page_size)  
        canvas.setLineWidth(25)
        canvas.setStrokeColorRGB(*color)
        canvas.line(x0, y0, x1, y1) 
        canvas.save()
        self.pdf.getPage(0).mergePage(PdfFileReader(BytesIO(document.getvalue())).getPage(0))

    def add_rect(self, x0, y0, x1, y1, color=[0, 0, 0, 0]):
        document = BytesIO()
        canvas = Canvas(document, pagesize=self.page_size)  
        canvas.setFillColorRGB(*color)
        canvas.rect(x0, y0, x1 - x0, y1 - y0, 0, 1) 
        canvas.save()
        self.pdf.getPage(0).mergePage(PdfFileReader(BytesIO(document.getvalue())).getPage(0))

    def add_note(self, src, x0, y0, comment='', author=''):
        self._add_image(src, x0, y0)
        self._add_highlight(x0, y0, 71, 39, comment, author)
  
    def export(self, fn, objects):
        funcs = {
            'LINE': self.add_line,
            'RECT': self.add_rect,
            'COMM': self.add_note,
        }
        for obj in objects['objects']:
            if funcs.get(obj['mode'], None):
                funcs[obj['mode']](**obj['attributes'])

        self.pdf.write(open(fn, 'wb'))

    def _add_image(self, source, x, y):
        if 'redactor/' not in source:
            source = 'redactor/' + source 
        document = BytesIO()
        canvas = Canvas(document, pagesize=self.page_size)
        canvas.setFillColorRGB(1, 1, 1)
        canvas.drawImage(source, x, y, mask='auto')
        canvas.save()
        self.pdf.getPage(0).mergePage(PdfFileReader(BytesIO(document.getvalue())).getPage(0))

    def _create_highlight(self, x0, y0, width, height, comment, author='', color=[0, 0, 0, 0]):
        self.add_rect(x0, y0, width, height)
        highlight = DictionaryObject()

        highlight.update({
            NameObject("/F"): NumberObject(4),
            NameObject("/Type"): NameObject("/Annot"),
            NameObject("/Subtype"): NameObject("/Highlight"),

            NameObject("/T"): TextStringObject(author),
            NameObject("/Contents"): TextStringObject(comment),

            NameObject("/C"): ArrayObject([FloatObject(c) for c in color]),
            NameObject("/Rect"): ArrayObject([
                FloatObject(x0),
                FloatObject(y0),
                FloatObject(x0 + width),
                FloatObject(y0 + width)
            ]),
            NameObject("/QuadPoints"): ArrayObject([
                FloatObject(x0),
                FloatObject(y0 + width),
                FloatObject(x0 + width),
                FloatObject(y0 + width),
                FloatObject(x0),
                FloatObject(y0),
                FloatObject(x0 + width),
                FloatObject(y0)
            ]),
        })

        return highlight

    def _add_highlight(self, x0, y0, width, height, comment, author='', color = [0, 0, 0, 0]):
        highlight = self._create_highlight(x0, y0, width, height, comment, author, color)
        highlight_ref = self.pdf._addObject(highlight)

        if "/Annots" in self.pdf.getPage(0):
            self.pdf.getPage(0)[NameObject("/Annots")].append(highlight_ref)
        else:
            self.pdf.getPage(0)[NameObject("/Annots")] = ArrayObject([highlight_ref])
        
        