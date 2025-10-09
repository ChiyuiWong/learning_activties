"""
COMP5241 Group 10 - Learning Activities Module Services
Responsible: Charlie
"""
import sys

# Prefer normal package import. If a test registers a stub module under the
# package path (e.g. 'app.modules.learning_activities.models') we'll use that
# instead. This avoids fragile file-path imports while still allowing tests to
# inject simple stand-ins.
try:
    from .models import LearningActivity, ActivitySubmission, ActivityProgress
except Exception:
    models_mod_name = 'app.modules.learning_activities.models'
    if models_mod_name in sys.modules:
        la_models = sys.modules[models_mod_name]
        LearningActivity = la_models.LearningActivity
        ActivitySubmission = la_models.ActivitySubmission
        ActivityProgress = la_models.ActivityProgress
    else:
        # Re-raise the original import error so missing package dependencies
        # surface immediately. Tests should install or register appropriate
        # stubs via sys.modules or run with the application package on PYTHONPATH.
        raise

from datetime import datetime
from typing import Any, List, Optional
from mongoengine.errors import DoesNotExist, ValidationError


class LearningActivityService:
    """Service class for learning activity operations.

    Methods return model instances when successful. They raise the
    underlying mongoengine exceptions (e.g. DoesNotExist, ValidationError)
    for the caller to handle, or ValueError for invalid inputs.
    """

    @staticmethod
    def create_activity(title: str, description: Optional[str], activity_type: Optional[str], course_id: str, created_by: str, **kwargs) -> Any:
        """Create and save a new LearningActivity.

        Accepts optional kwargs: instructions, max_score, time_limit (minutes),
        due_date (datetime or ISO string), is_active.
        Returns the created LearningActivity instance.
        """
        # Basic validation
        if not title or not str(title).strip():
            raise ValueError('Title is required')
        if not course_id or not str(course_id).strip():
            raise ValueError('course_id is required')
        if not created_by or not str(created_by).strip():
            raise ValueError('created_by is required')

        # Parse optional due_date
        due_date = kwargs.get('due_date')
        if isinstance(due_date, str):
            try:
                due_date = datetime.fromisoformat(due_date)
            except Exception:
                raise ValueError('due_date must be a datetime or ISO date string')

        activity = LearningActivity(
            title=str(title).strip(),
            description=str(description or '').strip(),
            activity_type=str(activity_type).strip() if activity_type else None,
            course_id=str(course_id).strip(),
            created_by=str(created_by).strip(),
            instructions=str(kwargs.get('instructions', '')).strip(),
            max_score=kwargs.get('max_score', 100),
            time_limit=kwargs.get('time_limit'),
            due_date=due_date,
            is_active=kwargs.get('is_active', True)
        )

        activity.save()
        return activity

    @staticmethod
    def get_activities_by_course(course_id: str, include_inactive: bool = False) -> Any:
        """Return a queryset/list of activities for a course.

        By default only returns active activities. Set include_inactive=True
        to include archived/closed activities.
        """
        if not course_id:
            raise ValueError('course_id is required')

        query = LearningActivity.objects.filter(course_id=course_id)
        if not include_inactive:
            query = query.filter(is_active=True)

        return query.order_by('-created_at')

    @staticmethod
    def get_activity_by_id(activity_id: str) -> Any:
        """Return a single LearningActivity or raise DoesNotExist."""
        if not activity_id:
            raise ValueError('activity_id is required')
        return LearningActivity.objects.get(id=activity_id)

    @staticmethod
    def submit_activity(activity_id: str, student_id: str, submission_data: Optional[dict]) -> Any:
        """Create a new ActivitySubmission for a given activity.

        Returns the saved ActivitySubmission instance.
        """
        if not activity_id or not student_id:
            raise ValueError('activity_id and student_id are required')

        activity = LearningActivity.objects.get(id=activity_id)

        # Basic checks
        if not activity.is_active:
            raise ValidationError('Activity is closed')
        if activity.due_date and activity.due_date < datetime.utcnow():
            raise ValidationError('Activity is past its due date')

        submission = ActivitySubmission(
            activity_id=str(activity.id),
            student_id=str(student_id),
            submission_data=submission_data or {},
            status='submitted',
            submitted_at=datetime.utcnow()
        )
        submission.save()
        return submission

    @staticmethod
    def grade_submission(submission_id: str, score: Optional[float] = None, feedback: Optional[str] = None, graded_by: Optional[str] = None) -> Any:
        """Grade an existing submission. Returns the updated submission.

        score should be numeric between 0 and 100. graded_by is the teacher id.
        """
        if not submission_id:
            raise ValueError('submission_id is required')

        submission = ActivitySubmission.objects.get(id=submission_id)

        if score is not None:
            try:
                score_val = float(score)
            except Exception:
                raise ValueError('score must be a number')
            if score_val < 0 or score_val > 100:
                raise ValueError('score must be between 0 and 100')
            submission.score = score_val

        if feedback is not None:
            submission.feedback = str(feedback)

        if graded_by:
            submission.graded_by = str(graded_by)

        submission.graded_at = datetime.utcnow()
        submission.status = 'graded'
        submission.save()
        return submission

    @staticmethod
    def update_progress(activity_id: str, student_id: str, progress_percentage: int = 0, time_spent: int = 0) -> Any:
        """Upsert ActivityProgress for a student and activity.

        progress_percentage: 0-100
        time_spent: minutes to add (int)
        Returns the ActivityProgress instance.
        """
        if not activity_id or not student_id:
            raise ValueError('activity_id and student_id are required')

        if progress_percentage is None:
            progress_percentage = 0
        try:
            progress_percentage = int(progress_percentage)
        except Exception:
            raise ValueError('progress_percentage must be integer 0-100')
        if progress_percentage < 0 or progress_percentage > 100:
            raise ValueError('progress_percentage must be between 0 and 100')

        try:
            time_spent = int(time_spent or 0)
        except Exception:
            raise ValueError('time_spent must be an integer (minutes)')

        prog = ActivityProgress.objects(activity_id=activity_id, student_id=student_id).first()
        if not prog:
            prog = ActivityProgress(
                activity_id=str(activity_id),
                student_id=str(student_id),
                progress_percentage=progress_percentage,
                time_spent=time_spent,
                last_accessed=datetime.utcnow(),
                is_completed=(progress_percentage >= 100)
            )
        else:
            # Update fields incrementally
            prog.progress_percentage = max(prog.progress_percentage, progress_percentage)
            prog.time_spent = prog.time_spent + time_spent
            prog.last_accessed = datetime.utcnow()
            if progress_percentage >= 100:
                prog.is_completed = True

        prog.save()
        return prog

    @staticmethod
    def get_student_progress(student_id: str, course_id: Optional[str] = None) -> Any:
        """Return student's progress records. If course_id provided, filter by activities in that course."""
        if not student_id:
            raise ValueError('student_id is required')

        progresses = ActivityProgress.objects.filter(student_id=student_id)

        if course_id:
            # Filter progresses by checking the related activity's course_id
            activity_ids = [str(a.id) for a in LearningActivity.objects.filter(course_id=course_id)]
            progresses = progresses.filter(activity_id__in=activity_ids)

        # If the returned object is a queryset-like with order_by, use it.
        if hasattr(progresses, 'order_by'):
            return progresses.order_by('-last_accessed')

        # If it's a plain list (as in some tests), sort and return the list
        if isinstance(progresses, list):
            return sorted(progresses, key=lambda p: getattr(p, 'last_accessed', None) or datetime.min, reverse=True)

        return progresses

    @staticmethod
    def get_submissions_for_grading(teacher_id: str, course_id: Optional[str] = None) -> Any:
        """Return submissions in status 'submitted' for activities created by teacher_id.

        If course_id provided, limit to that course.
        """
        if not teacher_id:
            raise ValueError('teacher_id is required')

        # Find activities created by this teacher
        activity_query = LearningActivity.objects.filter(created_by=teacher_id)
        if course_id:
            activity_query = activity_query.filter(course_id=course_id)

        activity_ids = [str(a.id) for a in activity_query]

        if not activity_ids:
            return []

        submissions = ActivitySubmission.objects.filter(activity_id__in=activity_ids, status='submitted').order_by('submitted_at')
        return submissions

    @staticmethod
    def get_submissions_for_activity(activity_id: str, teacher_id: Optional[str] = None) -> Any:
        """Return submissions for a specific activity. If teacher_id provided,
        you may enforce teacher ownership in the route using the activity record.
        """
        if not activity_id:
            raise ValueError('activity_id is required')

        submissions = ActivitySubmission.objects.filter(activity_id=str(activity_id)).order_by('submitted_at')
        return submissions
