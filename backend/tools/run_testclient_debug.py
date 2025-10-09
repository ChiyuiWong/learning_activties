from app import create_app
from app.config.config import TestConfig

app = create_app(TestConfig)
with app.test_client() as client:
    # Login
    r = client.post('/api/security/login', json={'username':'teacher1','password':'password123'})
    print('login status', r.status_code)
    print('login json', r.get_data(as_text=True))
    if r.status_code != 200:
        raise SystemExit('login failed')
    token = r.get_json().get('access_token')
    # Create poll
    headers = {'Authorization': f'Bearer {token}'}
    poll = {'question':'TC test','options':['A','B','C'],'course_id':'COMP5241'}
    r2 = client.post('/api/learning/polls', json=poll, headers=headers)
    print('create status', r2.status_code)
    try:
        print('create json:', r2.get_json())
    except Exception:
        print('create text:', r2.get_data(as_text=True))
