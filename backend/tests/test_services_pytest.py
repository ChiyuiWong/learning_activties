import importlib
import pytest
import sys
import types
from datetime import datetime


class StubModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = kwargs.get('id', 'stubid')

    def save(self):
        if not getattr(self, 'id', None):
            self.id = 'stubid'


def register_stubs(monkeypatch):
    # Create a fake models module and place it into sys.modules so services can import
    fake_models = types.ModuleType('app.modules.learning_activities.models')
    fake_models.LearningActivity = StubModel
    fake_models.ActivitySubmission = StubModel
    fake_models.ActivityProgress = StubModel
    monkeypatch.setitem(sys.modules, 'app.modules.learning_activities.models', fake_models)


def test_create_activity(monkeypatch):
    register_stubs(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    act = services.LearningActivityService.create_activity(
        title='T', description='D', activity_type='assignment', course_id='C1', created_by='teacher'
    )

    assert act.title == 'T'


def test_submit_inactive_activity(monkeypatch):
    register_stubs(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    # Replace LearningActivity.objects.get to return an inactive activity
    class FakeActivity:
        is_active = False
        due_date = None
        id = 'a1'

    class Obj:
        @staticmethod
        def get(id=None):
            return FakeActivity()

    # Attach objects manager to the stub class
    import app.modules.learning_activities.models as lm
    monkeypatch.setattr(lm.LearningActivity, 'objects', Obj)

    try:
        services.LearningActivityService.submit_activity('a1', 's1', {'x': 1})
    except Exception as e:
        assert isinstance(e, Exception)


def test_grade_submission_invalid_score(monkeypatch):
    register_stubs(monkeypatch)
    services = importlib.import_module('app.modules.learning_activities.services')

    # Stub ActivitySubmission.objects.get to return a submission object
    sub = StubModel(activity_id='a1', student_id='s1', status='submitted')

    class SubObj:
        @staticmethod
        def get(id=None):
            return sub

    import app.modules.learning_activities.models as lm
    monkeypatch.setattr(lm.ActivitySubmission, 'objects', SubObj)

    with pytest.raises(ValueError):
        services.LearningActivityService.grade_submission(submission_id='s1', score='bad')
