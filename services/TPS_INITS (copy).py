import os
import os.path
import pickle
import codecs 

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from csv_xlsx import convert

INPUT_DIR = 'inputs/'
MODE = 'AUTO'

def local_file_listing():
    files = os.listdir(INPUT_DIR)
    print('Escolha um arquivo para gerar a análise de destratores: (1 ... {})'.format(len(files)))
    for index, fn in enumerate(files):
        print('\t{}. {}'.format(index + 1, fn))
    
    choice = int(input('Arquivo: '))
    while choice < 1 or choice > len(files):
        choice = int(input('Tente novamente: '))

    return files[choice - 1]

def download_csv_files():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    """Shows basic usage of the Drive Activity API.

    Prints information about the last 10 events that occured the user's Drive.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('credentials/token'):
        with open('credentials/token', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('credentials/token', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v2', credentials=creds)

    HEADERS = b'"xA","xB","xC","xD","Q01","Q02","Q03","Q04","Q05","Q06","Q07","Q08","Q09","Q10"'
    # Call the Drive Activity API
    results = service.files().list().execute()
    for item in results['items']:
        if '(respostas)' in item['title']:
            print('[DOWNLOADING]::{}'.format(item['title'].replace('(respostas)', '').strip()), end='')
            data = service.files().export(fileId=item['id'], mimeType='text/csv').execute()
            # if non-empty file
            if data:
                with open('inputs/' + item['title'] + '.csv', 'wb') as f:
                    f.write(b'\n'.join([HEADERS] + data.split(b'\n')[1:]))
                print('')

def main():
    fn = None
    if MODE == 'SINGLE':
        fn = local_file_listing()
        convert(INPUT_DIR + fn)
    elif MODE == 'AUTO':
        # download_csv_files()

        files = os.listdir(INPUT_DIR)
        for _, fn in enumerate(sorted(files)):
            convert(INPUT_DIR + fn)
    
if __name__ == '__main__':
    main()