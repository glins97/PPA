from .essay import Essay
from .redaction import Redaction
from .student import Student

def essays_upload_to(essay, a):
    file_format = a[-3:]
    return 'uploads/essays/{}-{}-{}.{}'.format(essay.student.name, essay.student.school, essay.upload_date, file_format)

def redactions_upload_to(redaction, a):
    return 'uploads/redactions/[CORRECAO]-{}-{}-{}.pdf'.format(redaction.essay.student.name, redaction.essay.student.school, redaction.essay.upload_date)
