import os
import os.path
import pickle
import codecs 
import io
import re

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import openpyxl 
import pandas
import numpy as np
import os 
from copy import copy, deepcopy
import datetime

def get_row(cell):
    return int(re.search(r'(\d+?)$', cell).group(1))
    
def name_format(fn):
    return ' TPS '.join(fn.split('TPS')).replace('(respostas)', '').strip()

def auth():
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = None
    if os.path.exists('./destrator/credentials/token'):
        with open('./destrator/credentials/token', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './destrator/credentials/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('./destrator/credentials/token', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v2', credentials=creds)
    return service

def retrieve_drive_files():
    service = auth()
    results = service.files().list().execute()
    files = []
    for item in results['items']:
        if '(respostas)' in item['title']:
            files.append(item)
    return files

def download_csv_file(id):
    service = auth()
    HEADERS = b'"xA","xB","xC","xD","Q01","Q02","Q03","Q04","Q05","Q06","Q07","Q08","Q09","Q10"'
    for item in retrieve_drive_files():
        if item['id'] == id:
            data = service.files().export(fileId=item['id'], mimeType='text/csv').execute()
            data = b'\n'.join([HEADERS] + data.split(b'\n')[1:])
            print('@download_csv_file', item['title'])
            return item['title'], io.BytesIO(data)

def load_csv(fn):
    df = pandas.read_csv(fn)
    df['xC'] = df['xC'].str.replace(' / 10', '').astype(float) 
    return df 

def top_students(df, ammount=10):
    df = df.sort_values(by=['xC'])[::-1][:ammount]
    return df

def bottom_students(df, ammount=10):
    df = df.sort_values(by=['xC'])[:ammount]
    return df

def calculate_statistics(df):
    statistics = {}
    statistics['MEAN'] = np.mean(df['xC'])
    statistics['STD'] = np.std(df['xC'])
    for question_id in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']:
        question_title = 'Q{}'.format(question_id)        
        answers = {'A': 0, 'B': 0, 'C': 0, 'D':0, 'E': 0}
        for _, student_data in df.iterrows():
            if student_data[question_title] in answers:
                answers[student_data[question_title]] += 1
            else:
                answers[student_data[question_title]] = 1
        statistics[question_title] = answers
    return statistics

def print_statistics(data, title=''):
    print('STATISTICS OF {} STUDENTS:'.format(title))
    for key in data:
        print('    {}: {}'.format(key, data[key]))
    print()

def clear(ws, destination):
    ws[destination].font = copy(ws['A1'].font)
    ws[destination].border = copy(ws['A1'].border)
    ws[destination].fill = copy(ws['A1'].fill)
    ws[destination].number_format = copy(ws['A1'].number_format)
    ws[destination].protection = copy(ws['A1'].protection)
    ws[destination].alignment = copy(ws['A1'].alignment)
    ws[destination].style = copy(ws['A1'].style)
    if type(ws[destination]).__name__ != 'MergedCell':
        ws[destination].value = copy(ws['A1'].value)
    ws.row_dimensions[get_row(destination)].height = 30

def duplicate(ws, origin, destination):
    ws[destination].font = copy(ws[origin].font)
    ws[destination].border = copy(ws[origin].border)
    ws[destination].fill = copy(ws[origin].fill)
    ws[destination].number_format = copy(ws[origin].number_format)
    ws[destination].protection = copy(ws[origin].protection)
    ws[destination].alignment = copy(ws[origin].alignment)
    if type(ws[destination]).__name__ != 'MergedCell':
        ws[destination].value = copy(ws[origin].value)

    if (ws.row_dimensions[get_row(origin)].height == 7.5):
        ws.row_dimensions[get_row(destination)].height = 7.5

def move(ws, origin, destination):
    duplicate(ws, origin, destination)
    clear(ws, origin)

def convert(fn, fdata=None):
    print('@CONVERT>>', fn, fdata)
    fn_formatted = fn.replace('inputs/', '').replace('(respostas)', '').replace('.csv', '').replace('.xlsx', '').replace('-', '').replace('  ', ' ').strip()
    
    df = load_csv(fdata if fdata else fn)
    print('CONVERT>>SHAPE::', df.shape)
    print('CONVERT>>GENERATING REPORT::{}'.format(fn_formatted))
    top = top_students(df)
    bot = bottom_students(df)[::-1]
    # rest = pandas.concat([df, top]).drop_duplicates(keep=False)
    # rest = pandas.concat([rest, bot]).drop_duplicates(keep=False).sort_values(by=['xC'])[::-1]
    all_stats = calculate_statistics(df)
    # print_statistics(all_stats, 'ALL')
    
    wb = openpyxl.load_workbook(filename='destrator/inputs/TEMPLATE.xlsx')
    ws = wb.active
    ws['B3'] = fn_formatted
    ws['G3'] = datetime.datetime.now().strftime('%d/%m/%Y')
    ws['D6'] = '{:.2f}'.format(all_stats['MEAN'])
    ws['F6'] = '{:.2f}'.format(all_stats['STD'])

    # title
    ws.merge_cells('C4:F4')

    matrix_base_row = 19
    if df.shape[0] >= 10:

        # move tables
        matrix_base_row += 9
        for row in range(29, 11, -1):
            for column in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
                move(ws, column + str(row), column + str(row + 9))
        
        # top students filling
        students = list(top.iterrows())
        ws['G10'] = students[0][1]['xC']
        ws['C10'] = students[0][1]['xD'].upper()
        ws['B10'] = '1.  '
        ws['B10'].alignment = openpyxl.styles.Alignment(horizontal='right', vertical='center')
        ws['B10'].border = copy(ws['B5'].border)
        ws['C10'].border = copy(ws['C5'].border)
        ws['D10'].border = copy(ws['D5'].border)
        ws['E10'].border = copy(ws['E5'].border)
        ws['F10'].border = copy(ws['F5'].border)
        ws['G10'].border = copy(ws['G5'].border)
        for index, (_, student) in enumerate(students[1:]):
            row = str(11 + index)
            duplicate(ws, 'C10', 'C' + row)
            duplicate(ws, 'G10', 'G' + row)
            ws['C' + row].border = copy(ws['A1'].border)
            ws['B' + row].border = copy(ws['B5'].border)
            ws['G' + row].border = copy(ws['G5'].border)
            ws['G' + row] = student['xC']
            ws['C' + row] = student['xD'].upper()
            ws['B' + row] = '{}.  '.format(index + 2)
            ws['B' + row].alignment = openpyxl.styles.Alignment(horizontal='right', vertical='center')
            if type(ws['C' + row]).__name__ != 'MergedCell':
                ws.merge_cells('C{}:F{}'.format(row, row))
        ws['B19'].border = copy(ws['B6'].border)
        ws['C19'].border = copy(ws['C6'].border)
        ws['D19'].border = copy(ws['D6'].border)
        ws['E19'].border = copy(ws['E6'].border)
        ws['F19'].border = copy(ws['F6'].border)
        ws['G19'].border = copy(ws['G6'].border)

    if df.shape[0] >= 20:
        # move tables
        matrix_base_row += 9
        for row in range(38, 24, -1):
            for column in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
                move(ws, column + str(row), column + str(row + 9))

        # bottom students filling
        students = list(bot.iterrows())
        ws['G23'] = students[0][1]['xC']
        ws['C23'] = students[0][1]['xD'].upper()
        ws['B23'] = '{}.  '.format(df.shape[0] - 10)
        ws['B23'].alignment = openpyxl.styles.Alignment(horizontal='right', vertical='center')
        ws['B23'].border = copy(ws['B5'].border)
        ws['C23'].border = copy(ws['C5'].border)
        ws['D23'].border = copy(ws['D5'].border)
        ws['E23'].border = copy(ws['E5'].border)
        ws['F23'].border = copy(ws['F5'].border)
        ws['G23'].border = copy(ws['G5'].border)
        ws.merge_cells('C23:F23')
        for index, (_, student) in enumerate(students[1:]):
            row = str(24 + index)
            duplicate(ws, 'C23', 'C' + row)
            duplicate(ws, 'G23', 'G' + row)
            ws['C' + row].border = copy(ws['A5'].border)
            ws['B' + row].border = copy(ws['B5'].border)
            ws['D' + row].border = copy(ws['D5'].border)
            ws['E' + row].border = copy(ws['E5'].border)
            ws['F' + row].border = copy(ws['F5'].border)
            ws['G' + row].border = copy(ws['G5'].border)
            ws['G' + row] = student['xC']
            ws['C' + row] = student['xD'].upper()
            ws['B' + row] = '{}.  '.format(df.shape[0] - 10 + index + 1)
            ws['B' + row].alignment = openpyxl.styles.Alignment(horizontal='right', vertical='center')
            if type(ws['C' + row]).__name__ != 'MergedCell':
                ws.merge_cells('C{}:F{}'.format(row, row))
        ws['B32'].border = copy(ws['B6'].border)
        ws['C32'].border = copy(ws['C6'].border)
        ws['D32'].border = copy(ws['D6'].border)
        ws['E32'].border = copy(ws['E6'].border)
        ws['F32'].border = copy(ws['F6'].border)
        ws['G32'].border = copy(ws['G6'].border)
    
    # destractor matrix header
    ws.merge_cells('D{}:F{}'.format(matrix_base_row-2, matrix_base_row-2))
    
    # destractor matrix
    for index, question_id in enumerate(['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']):
        question_title = 'Q{}'.format(question_id)
        answers = ['A', 'B', 'C', 'D', 'E']
        for a_index, answer in enumerate(answers):
            ws[chr(ord('C') + a_index).upper() + str(matrix_base_row + index)] = all_stats[question_title][answer]

    wb.save('destrator/outputs/' + fn_formatted.upper() + '_RELATORIO.xlsx')
    return 'destrator/outputs/' + fn_formatted.upper() + '_RELATORIO.xlsx'



