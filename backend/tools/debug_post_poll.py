from app import create_app
from app.config.config import TestConfig
import json


def main():
    app = create_app(TestConfig)
    client = app.test_client()
    headers = {'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZWFjaGVyMSIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoxODAwMDAwMDAwfQ.mock'}
    body = {'question': 'What is your favorite language?', 'options': ['Python', 'JS'], 'course_id': 'TEST_COURSE'}
    resp = client.post('/api/learning/polls', headers=headers, data=json.dumps(body), content_type='application/json')
    print('status', resp.status_code)
    try:
        print(resp.get_json())
    except Exception:
        print(resp.data.decode())


if __name__ == '__main__':
    main()
