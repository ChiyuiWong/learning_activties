import requests
import sys
from pprint import pprint

BASE_URL = 'http://localhost:5000/api'
TEACHER_CREDENTIALS = {'username': 'teacher1','password':'password123'}

try:
    resp = requests.post(f'{BASE_URL}/security/login', json=TEACHER_CREDENTIALS, timeout=5)
    print('login status', resp.status_code)
    print(resp.text)
    if resp.status_code != 200:
        sys.exit(1)
    token = resp.json().get('access_token')
    poll_data = {'question':'What is your favourite?','options':['A','B','C'],'course_id':'COMP5241'}
    r = requests.post(f'{BASE_URL}/learning/polls', headers={'Authorization':f'Bearer {token}'}, json=poll_data, timeout=5)
    print('create status', r.status_code)
    try:
        pprint(r.json())
    except Exception:
        print(r.text)
except Exception as e:
    print('error', e)

