from datetime import datetime
import importlib
import os
import sys


# Insert a lightweight fake 'models' module into sys.modules so services.py can
# import from '.models' without requiring mongoengine. Tests will monkeypatch
# svc.LearningActivity / ActivitySubmission / ActivityProgress as needed.
import sys
import types
fake_models = types.ModuleType('app.modules.learning_activities.models')

class _Stub:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = None
    def save(self):
        if not getattr(self, 'id', None):
            self.id = 'stubid'

fake_models.LearningActivity = _Stub
fake_models.ActivitySubmission = _Stub
fake_models.ActivityProgress = _Stub

# Ensure sys.modules path for the relative import used in services.py
sys.modules['app.modules.learning_activities.models'] = fake_models

svc_path = os.path.join(os.path.dirname(__file__), 'services.py')
spec = importlib.util.spec_from_file_location('services', svc_path)
svc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(svc)

# Use ValidationError from the services module (it provides a fallback when
# mongoengine isn't installed)
ValidationError = getattr(svc, 'ValidationError', Exception)


class raises:
    """Simple context manager similar to pytest.raises"""
    def __init__(self, exc_type):
        self.exc_type = exc_type

    def __enter__(self):
        return None

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            raise AssertionError(f"Expected exception {self.exc_type.__name__} not raised")
        return issubclass(exc_type, self.exc_type)


class DummySaved:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.id = None

    def save(self):
        # emulate assigning an id and created_at when saving
        if not getattr(self, 'id', None):
            self.id = 'mockid'
        if not getattr(self, 'created_at', None):
            self.created_at = datetime.utcnow()


def test_create_activity_success(monkeypatch):
    """Creating an activity should return the saved activity instance."""

    def fake_init(self, **kwargs):
        # store kwargs as attributes
        for k, v in kwargs.items():
            setattr(self, k, v)

    # Replace LearningActivity class with DummySaved-like behavior
    monkeypatch.setattr(svc, 'LearningActivity', DummySaved)

    act = svc.LearningActivityService.create_activity(
        title='Test',
        description='Desc',
        activity_type='assignment',
        course_id='COURSE1',
        created_by='teacher1'
    )

    assert isinstance(act, DummySaved)
    assert act.id == 'mockid'
    assert act.title == 'Test'


def test_submit_activity_closed_activity(monkeypatch):
    """Submitting to a closed activity should raise ValidationError."""

    class FakeActivity:
        def __init__(self):
            self.is_active = False
            self.due_date = None
            self.id = 'a1'

    class ObjManager:
        @staticmethod
        def get(id=None):
            return FakeActivity()

    monkeypatch.setattr(svc, 'LearningActivity', svc.LearningActivity)
    # attach fake objects manager
    monkeypatch.setattr(svc.LearningActivity, 'objects', ObjManager, raising=False)

    with raises(ValidationError):
        svc.LearningActivityService.submit_activity('a1', 'student1', {'ans': 1})


def test_grade_submission_invalid_score(monkeypatch):
    """Grading with a non-numeric or out-of-range score should raise ValueError."""

    sub = DummySaved(activity_id='a1', student_id='s1', status='submitted')

    class SubManager:
        @staticmethod
        def get(id=None):
            return sub

    monkeypatch.setattr(svc, 'ActivitySubmission', DummySaved)
    monkeypatch.setattr(svc.ActivitySubmission, 'objects', SubManager, raising=False)

    # non-numeric
    with raises(ValueError):
        svc.LearningActivityService.grade_submission(submission_id='s1', score='bad')

    # out of range
    with raises(ValueError):
        svc.LearningActivityService.grade_submission(submission_id='s1', score=150)


def test_grade_submission_success(monkeypatch):
    # prepare a submission stub
    sub = DummySaved(activity_id='a1', student_id='s1', status='submitted')

    class SubManager:
        @staticmethod
        def get(id=None):
            return sub

    monkeypatch.setattr(svc, 'ActivitySubmission', DummySaved)
    monkeypatch.setattr(svc.ActivitySubmission, 'objects', SubManager, raising=False)

    updated = svc.LearningActivityService.grade_submission(submission_id='s1', score=85, feedback='Good', graded_by='t1')
    assert updated.score == 85
    assert updated.status == 'graded'


def test_get_student_progress_empty(monkeypatch):
    # Setup ActivityProgress.objects.filter(...).order_by to return empty list
    class ProgManager:
        @staticmethod
        def filter(student_id=None):
            return []

    monkeypatch.setattr(svc, 'ActivityProgress', DummySaved)
    monkeypatch.setattr(svc.ActivityProgress, 'objects', ProgManager, raising=False)

    progs = svc.LearningActivityService.get_student_progress('stud1')
    assert progs == []


def test_update_progress_creates_new(monkeypatch):
    """When no progress exists, update_progress should create and return a new record."""

    # Ensure ActivityProgress.objects(...).first() returns None
    # Provide an objects callable that returns a query-like object with a
    # .first() method that returns None (no existing progress)
    class QObj:
        @staticmethod
        def first():
            return None

    monkeypatch.setattr(svc, 'ActivityProgress', DummySaved)
    monkeypatch.setattr(svc.ActivityProgress, 'objects', lambda activity_id=None, student_id=None: QObj(), raising=False)

    prog = svc.LearningActivityService.update_progress('act1', 'stud1', progress_percentage=30, time_spent=10)

    assert isinstance(prog, DummySaved)
    assert prog.progress_percentage == 30
    assert prog.time_spent == 10
    assert prog.is_completed is False
