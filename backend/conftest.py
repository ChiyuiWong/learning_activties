import pytest

from app import create_app
from app.config.config import TestConfig


@pytest.fixture(scope='session')
def app():
    app = create_app(config_class=TestConfig)
    yield app


@pytest.fixture(scope='session')
def client(app):
    return app.test_client()


def _make_test_token(username: str, role: str) -> str:
    import base64, json
    payload = json.dumps({"sub": username, "role": role})
    b = base64.urlsafe_b64encode(payload.encode('utf-8')).decode('utf-8').rstrip('=')
    return f"header.{b}.signature"


@pytest.fixture(scope='session')
def teacher_token(app):
    return _make_test_token('teacher1', 'teacher')


@pytest.fixture(scope='session')
def student_token(app):
    return _make_test_token('student1', 'student')


@pytest.fixture(scope='function')
def poll_id(client, teacher_token):
    headers = {'Authorization': f'Bearer {teacher_token}'}
    payload = {
        'question': 'Test poll?',
        'options': ['Yes', 'No'],
        'course_id': 'CS101'
    }
    resp = client.post('/api/learning/polls', json=payload, headers=headers)
    if resp.status_code != 201:
        raise RuntimeError(f"Failed to create poll for tests: {resp.status_code} {resp.data}")
    data = resp.get_json()
    return data.get('poll_id')
