from io import BytesIO
from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def assign_grades(source, destination, grade_1, grade_2, grade_3, grade_4, grade_5):
    pdf = PdfFileWriter()
    imgTemp = BytesIO()
    imgDoc = canvas.Canvas(imgTemp, pagesize=A4)
    imgDoc.drawImage('grade_1.png', 105 + 97 * 0, 555, 23, 5 + grade_to_px(grade_1))
    imgDoc.drawImage('grade_2.png', 105 + 97 * 1, 555, 23, 5 + grade_to_px(grade_2))
    imgDoc.drawImage('grade_3.png', 105 + 97 * 2, 555, 23, 5 + grade_to_px(grade_3))
    imgDoc.drawImage('grade_4.png', 105 + 97 * 3, 555, 23, 5 + grade_to_px(grade_4))
    imgDoc.drawImage('grade_5.png', 105 + 97 * 4, 555, 23, 5 + grade_to_px(grade_5))
    imgDoc.save()
    page = PdfFileReader(open(source, 'rb')).getPage(-1)
    overlay = PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0)
    page.mergePage(overlay)
    output = PdfFileWriter()
    output.addPage(page)
    output.write(open(destination, 'wb'))

def grade_to_px(value):
    if value == 200:
        value = 218
    return value * 160.0/200