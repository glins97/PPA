import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.encoders import encode_base64
import codecs
from threading import _start_new_thread

def send_mail(email, subject, message, attachment):
    def _send_mail(email, subject, message, attachment):
        msg = MIMEMultipart()
        password = 'campusppa'
        msg['To'] = email
        msg['From'] = 'adm.ppa.digital@gmail.com'
        msg['Subject'] = 'PPA Digital: ' + subject

        if attachment:
            openedfile = None
            with open(attachment, 'rb') as opened:
                openedfile = opened.read()
            attachedfile = MIMEApplication(openedfile, _subtype = "pdf", _encoder=encode_base64)
            attachedfile.add_header('content-disposition', 'attachment', filename=attachment.split('/')[-1])
            msg.attach(attachedfile)

        with smtplib.SMTP('smtp.gmail.com: 587') as server:
            server.starttls()
            server.login(msg['From'], password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())
    try:
        _start_new_thread(_send_mail, (email, subject, message, attachment))
        return True
    except Exception as e:
        print('exception @send_mail ->', e)
        return False

def _pushed_notify(content):
    if not content:
        return

    payload = {
        'app_key': 'BuOsbbNilU2hbuykX9Mq',
        'app_secret': 'NTq1qC7giKAUEnDK6RLz0gCuVDxOYHoZDtCp7mX314YseFomkYo6gg6s9BReXfv4',
        'target_type': 'app',
        'content': content
    }
    requests.post('https://api.pushed.co/1/push', data=payload)