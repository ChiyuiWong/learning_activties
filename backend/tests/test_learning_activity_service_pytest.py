import importlib
import sys
import types
import pytest
from datetime import datetime


class StubModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = kwargs.get('id', 'stubid')

    def save(self):
        if not getattr(self, 'id', None):
            self.id = 'stubid'


def register_stub_models(monkeypatch):
    fake_models = types.ModuleType('app.modules.learning_activities.models')
    fake_models.LearningActivity = StubModel
    fake_models.ActivitySubmission = StubModel
    fake_models.ActivityProgress = StubModel
    monkeypatch.setitem(sys.modules, 'app.modules.learning_activities.models', fake_models)


def test_create_activity_success(monkeypatch):
    register_stub_models(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    # Replace LearningActivity with a dummy class that records attributes
    class DummySaved(StubModel):
        pass

    monkeypatch.setattr(services, 'LearningActivity', DummySaved)

    act = services.LearningActivityService.create_activity(
        title='Test', description='Desc', activity_type='assignment', course_id='C1', created_by='t1'
    )

    assert isinstance(act, DummySaved)


def test_submit_activity_closed_activity(monkeypatch):
    register_stub_models(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    class FakeActivity:
        is_active = False
        due_date = None
        id = 'a1'

    class Obj:
        @staticmethod
        def get(id=None):
            return FakeActivity()

    monkeypatch.setattr(services, 'LearningActivity', StubModel)
    monkeypatch.setattr(services.LearningActivity, 'objects', Obj, raising=False)

    with pytest.raises(Exception):
        services.LearningActivityService.submit_activity('a1', 's1', {'a': 1})


def test_grade_submission_invalid_score(monkeypatch):
    register_stub_models(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    sub = StubModel(activity_id='a1', student_id='s1', status='submitted')

    class SubObj:
        @staticmethod
        def get(id=None):
            return sub

    monkeypatch.setattr(services, 'ActivitySubmission', StubModel)
    monkeypatch.setattr(services.ActivitySubmission, 'objects', SubObj, raising=False)

    with pytest.raises(ValueError):
        services.LearningActivityService.grade_submission(submission_id='s1', score='bad')


def test_grade_submission_success(monkeypatch):
    register_stub_models(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    sub = StubModel(activity_id='a1', student_id='s1', status='submitted')

    class SubObj:
        @staticmethod
        def get(id=None):
            return sub

    monkeypatch.setattr(services, 'ActivitySubmission', StubModel)
    monkeypatch.setattr(services.ActivitySubmission, 'objects', SubObj, raising=False)

    updated = services.LearningActivityService.grade_submission(submission_id='s1', score=90, feedback='Good', graded_by='t1')
    assert updated.score == 90
    assert updated.status == 'graded'


def test_get_student_progress_empty(monkeypatch):
    register_stub_models(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    class ProgMgr:
        @staticmethod
        def filter(student_id=None):
            return []

    monkeypatch.setattr(services, 'ActivityProgress', StubModel)
    monkeypatch.setattr(services.ActivityProgress, 'objects', ProgMgr, raising=False)

    progs = services.LearningActivityService.get_student_progress('s1')
    assert progs == []


def test_update_progress_creates_new(monkeypatch):
    register_stub_models(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    class QObj:
        @staticmethod
        def first():
            return None

    monkeypatch.setattr(services, 'ActivityProgress', StubModel)
    monkeypatch.setattr(services.ActivityProgress, 'objects', lambda activity_id=None, student_id=None: QObj(), raising=False)

    prog = services.LearningActivityService.update_progress('a1', 's1', progress_percentage=40, time_spent=5)
    assert isinstance(prog, StubModel)
    assert prog.progress_percentage == 40
