from .essay import Essay
from .redaction import Redaction
from .school import School
from .student import Student
from .notification import NotificationConfiguration

def essays_upload_to(essay, a):
    file_format = a[-3:]
    return 'uploads/essays/{}-{}-{}.{}'.format(essay.student.name, essay.student.school.name, essay.upload_date, file_format)

def redactions_upload_to(redaction, a):
    return 'uploads/redactions/[CORRECAO]-{}-{}-{}.pdf'.format(redaction.essay.student.name, redaction.essay.student.school.name, redaction.essay.upload_date)
