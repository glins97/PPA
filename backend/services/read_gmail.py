import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import datetime
import os, django
import pandas

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "services.settings")
django.setup()
from essay_probono.models import Essay, Student
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.settings.basic',
    'https://www.googleapis.com/auth/gmail.settings.sharing',
]

import base64
from apiclient import errors

def upload_to(student, extension):
    return 'uploads/essays/SOLIDÁRIA-{}-{}.{}'.format(student.name, datetime.datetime.now(), extension[-3:]).replace(':', '-').replace(' ', '_')

def get_bd_obj(class_, **kwargs):
    objs = class_.objects.all().filter(**kwargs)
    if objs: return objs[0]
    obj = class_(**kwargs)
    obj.save()
    return obj

def get_attachments(service, msg_id, student):
    try:
        message = service.users().messages().get(userId='me', id=msg_id).execute()
        for part in message['payload'].get('parts', ''):
            if part['filename']:    
                if 'data' in part['body']:
                    data=part['body']['data']
                else:
                    att_id=part['body']['attachmentId']
                    att=service.users().messages().attachments().get(userId='me', messageId=msg_id,id=att_id).execute()
                    data=att['data']

        file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
        path = upload_to(student, part['filename'])
        with open(path, 'wb') as f:
            f.write(file_data)
        return path
    except UnboundLocalError as error:
        print(repr(error))
        return None

def main():
    creds = None
    if os.path.exists('essay_probono/credentials/token'):
        with open('essay_probono/credentials/token', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'essay_probono/credentials/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('essay_probono/credentials/token', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
    messages = results.get('messages', [])
    already_added = [ essay.mail_id for essay in Essay.objects.all() ]
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        subject_ = ''
        from_email = ''
        from_name = ''
        attachment = None
        message_id = message['id']
        if message_id in already_added: break

        for header in msg['payload']['headers']:
            if header['name'] == 'From':
                from_name, from_email = header['value'].split('<')
                from_name = from_name.strip().upper()
                from_email = from_email.replace('>', '')
            if header['name'] == 'Subject':
                subject_ = header['value'].lower()
        
        blocks = ['GOOGLE']
        skip = False
        for block in blocks:
            if block in from_name:
                skip = True
        if skip: continue
        choice = input('{} {} (Y/N) '.format(from_name, subject_))
        if choice.lower() == 'y':
            student = get_bd_obj(Student, name=from_name, email=from_email)
            attachment = get_attachments(service, message_id, student)
            if attachment:
                essay = get_bd_obj(Essay, mail_id=message_id, student=student, file=attachment)
                essay.save()

if __name__ == '__main__':
    main()