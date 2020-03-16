import datetime
import os, django
import pandas
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "services.settings")
django.setup()

from tps.models import Report
from tps.auxilliary import *

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle

# do login
driver = webdriver.Firefox()
driver.get('https://soundcloud.com/signin')
time.sleep(2)

gmail_login = driver.find_element_by_class_name('sc-button-google')
gmail_login.click()
time.sleep(2)

before, after = driver.window_handles[0], driver.window_handles[1]
driver.switch_to_window(after)

login = driver.find_element_by_id('identifierId')
login.send_keys('romullo.quimica')
login.send_keys(Keys.RETURN)
time.sleep(2)

password = driver.find_element_by_name('password')
password.send_keys('qazxsaq5601')
password.send_keys(Keys.RETURN)
time.sleep(2)
driver.switch_to_window(before)
# -------------------

# retrieve forms
result = []
page_token = None
while True:
    try:
        param = {}
        if page_token:
            param['pageToken'] = page_token
        files = service.files().list(**param).execute()
        for file_ in files['items']:
            if 'TPS' in file_['title'] and 'https://docs.google.com/forms' in file_['alternateLink']:
                result.append(file_)
                print('adding...', file_['title'])

        page_token = files.get('nextPageToken')
        if not page_token:
            break
    except e:
        print('An error occurred:', e)
        break
# -------------------

# gets correct answers
answers = {}
with open('answers', 'rb') as handle:
    answers = pickle.load(handle)

for tps in sorted(result, key=lambda item: item['title']):
    try:
        if name_format(tps['title']) in answers:
            continue

        print('GET', tps['title'], end=' -> ')
        url = 'https://docs.google.com/forms/d/{}/edit'.format(tps['id'])
        driver.get(url)
        time.sleep(1)

        title = driver.find_elements_by_class_name('freebirdFormeditorViewItemTitleRow')[1]
        title.click()

        time.sleep(1)
        check_answers_btn = driver.find_elements_by_class_name('freebirdFormeditorViewQuestionFooterWide')
        for item in check_answers_btn:
            if item.text == 'Chave de resposta':
                item.click()
                time.sleep(1)
                break

        form_answers = driver.find_elements_by_class_name('freebirdFormeditorViewAssessmentGridbodyCorrectAnswerToggle')
        correct_answers = ['ABCDE'[[answer.get_attribute('aria-checked') for answer in form_answers[i:i+5]].index('true')] for i in range(0, 50, 5)]
        form_correct_answers = {'correct_answer_' + str(i + 1): correct_answers[i] for i in range(0, 10)}
        answers[name_format(tps['title'])] = form_correct_answers
        print('DONE')
        with open('answers', 'wb') as handle:
            pickle.dump(answers, handle)
    except Exception as e:
        answers[name_format(tps['title'])] = None
        print('FAILED ->', e)
        with open('answers', 'wb') as handle:
            pickle.dump(answers, handle)
# -------------------

driver.close()
with open('answers', 'wb') as handle:
    pickle.dump(answers, handle)
