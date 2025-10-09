import threading
import time
import requests
import sys
from werkzeug.serving import make_server
from app import create_app
from app.config.config import TestConfig

class ServerThread(threading.Thread):
    def __init__(self, app, host='127.0.0.1', port=5000):
        super().__init__()
        self.srv = make_server(host, port, app)
        self.ctx = app.app_context()
        self.ctx.push()

    def run(self):
        self.srv.serve_forever()

    def shutdown(self):
        self.srv.shutdown()


def wait_ready(url, timeout=10.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=1.0)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def main():
    app = create_app(TestConfig)
    server = ServerThread(app)
    server.start()
    ready = wait_ready('http://127.0.0.1:5000/api/health', timeout=10.0)
    if not ready:
        print('Server did not become ready')
        server.shutdown()
        sys.exit(2)
    print('Server ready')

    BASE_URL = 'http://127.0.0.1:5000/api'
    teacher = {'username':'teacher1','password':'password123'}
    student = {'username':'student1','password':'password123'}
    try:
        print('\nLogging in as teacher...')
        r = requests.post(f'{BASE_URL}/security/login', json=teacher, timeout=5)
        print('teacher login status', r.status_code)
        print('teacher resp:', r.text)
        token = r.json().get('access_token') if r.status_code==200 else None

        print('\nCreating poll...')
        poll_data = {'question':'What is your favourite?','options':['A','B','C'],'course_id':'COMP5241'}
        r2 = requests.post(f'{BASE_URL}/learning/polls', headers={'Authorization':f'Bearer {token}'}, json=poll_data, timeout=5)
        print('create status', r2.status_code)
        try:
            print('create resp json:')
            print(r2.json())
        except Exception:
            print('create resp text:')
            print(r2.text)
    finally:
        server.shutdown()
        server.join()

if __name__ == '__main__':
    main()
