"""
COMP5241 Group 10 - Learning Activities Module Services
Responsible: Charlie
"""
from datetime import datetime
from typing import Any, List, Optional
from flask import current_app
from bson import ObjectId
from config.database import get_db_connection


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

        activity_data = {
            'title': str(title).strip(),
            'description': str(description or '').strip(),
            'activity_type': str(activity_type).strip() if activity_type else None,
            'course_id': str(course_id).strip(),
            'created_by': str(created_by).strip(),
            'instructions': str(kwargs.get('instructions', '')).strip(),
            'max_score': kwargs.get('max_score', 100),
            'time_limit': kwargs.get('time_limit'),
            'due_date': due_date,
            'is_active': kwargs.get('is_active', True),
            'created_at': datetime.utcnow()
        }

        with get_db_connection() as client:
            db = client['comp5241_g10']
            result = db.learning_activities.insert_one(activity_data)
        activity_data['_id'] = result.inserted_id
        return activity_data

    @staticmethod
    def get_activities_by_course(course_id: str, include_inactive: bool = False) -> Any:
        """Return a queryset/list of activities for a course.

        By default only returns active activities. Set include_inactive=True
        to include archived/closed activities.
        """
        if not course_id:
            raise ValueError('course_id is required')

        query = {'course_id': course_id}
        if not include_inactive:
            query['is_active'] = True

        with get_db_connection() as client:
            db = client['comp5241_g10']
            return list(db.learning_activities.find(query).sort('created_at', -1))

    @staticmethod
    def get_activity_by_id(activity_id: str) -> Any:
        """Return a single LearningActivity or raise DoesNotExist."""
        if not activity_id:
            raise ValueError('activity_id is required')
        with get_db_connection() as client:
            db = client['comp5241_g10']
            activity = db.learning_activities.find_one({'_id': ObjectId(activity_id)})
        if not activity:
            raise ValueError('Activity not found')
        return activity

    @staticmethod
    def submit_activity(activity_id: str, student_id: str, submission_data: Optional[dict]) -> Any:
        """Create a new ActivitySubmission for a given activity.

        Returns the saved ActivitySubmission instance.
        """
        if not activity_id or not student_id:
            raise ValueError('activity_id and student_id are required')

        with get_db_connection() as client:
            db = client['comp5241_g10']
            activity = db.learning_activities.find_one({'_id': ObjectId(activity_id)})
        if not activity:
            raise ValueError('Activity not found')

        # Basic checks
        if not activity.get('is_active', True):
            raise ValueError('Activity is closed')
        if activity.get('due_date') and activity['due_date'] < datetime.utcnow():
            raise ValueError('Activity is past its due date')

        submission_data = {
            'activity_id': str(activity_id),
            'student_id': str(student_id),
            'submission_data': submission_data or {},
            'status': 'submitted',
            'submitted_at': datetime.utcnow()
        }
        with get_db_connection() as client:
            db = client['comp5241_g10']
            result = db.activity_submissions.insert_one(submission_data)
        submission_data['_id'] = result.inserted_id
        return submission_data

    @staticmethod
    def grade_submission(submission_id: str, score: Optional[float] = None, feedback: Optional[str] = None, graded_by: Optional[str] = None) -> Any:
        """Grade an existing submission. Returns the updated submission.

        score should be numeric between 0 and 100. graded_by is the teacher id.
        """
        if not submission_id:
            raise ValueError('submission_id is required')

        with get_db_connection() as client:
            db = client['comp5241_g10']
            submission = db.activity_submissions.find_one({'_id': ObjectId(submission_id)})
        if not submission:
            raise ValueError('Submission not found')

        update_data = {}

        if score is not None:
            try:
                score_val = float(score)
            except Exception:
                raise ValueError('score must be a number')
            if score_val < 0 or score_val > 100:
                raise ValueError('score must be between 0 and 100')
            update_data['score'] = score_val

        if feedback is not None:
            update_data['feedback'] = str(feedback)

        if graded_by:
            update_data['graded_by'] = str(graded_by)

        update_data['graded_at'] = datetime.utcnow()
        update_data['status'] = 'graded'

        with get_db_connection() as client:
            db = client['comp5241_g10']
            db.activity_submissions.update_one(
                {'_id': ObjectId(submission_id)},
                {'$set': update_data}
            )

        # Return updated submission
        with get_db_connection() as client:
            db = client['comp5241_g10']
            return db.activity_submissions.find_one({'_id': ObjectId(submission_id)})

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

        # Check if progress record exists
        with get_db_connection() as client:
            db = client['comp5241_g10']
            existing_progress = db.activity_progress.find_one({
                'activity_id': str(activity_id),
                'student_id': str(student_id)
            })

        if not existing_progress:
            progress_data = {
                'activity_id': str(activity_id),
                'student_id': str(student_id),
                'progress_percentage': progress_percentage,
                'time_spent': time_spent,
                'last_accessed': datetime.utcnow(),
                'is_completed': (progress_percentage >= 100)
            }
            with get_db_connection() as client:
                db = client['comp5241_g10']
                result = db.activity_progress.insert_one(progress_data)
            progress_data['_id'] = result.inserted_id
            return progress_data
        else:
            # Update fields incrementally
            update_data = {
                'progress_percentage': max(existing_progress.get('progress_percentage', 0), progress_percentage),
                'time_spent': existing_progress.get('time_spent', 0) + time_spent,
                'last_accessed': datetime.utcnow()
            }
            if progress_percentage >= 100:
                update_data['is_completed'] = True

            with get_db_connection() as client:
                db = client['comp5241_g10']
                db.activity_progress.update_one(
                    {'_id': existing_progress['_id']},
                    {'$set': update_data}
                )

            # Return updated progress
            with get_db_connection() as client:
                db = client['comp5241_g10']
                return db.activity_progress.find_one({'_id': existing_progress['_id']})

    @staticmethod
    def get_student_progress(student_id: str, course_id: Optional[str] = None) -> Any:
        """Return student's progress records. If course_id provided, filter by activities in that course."""
        if not student_id:
            raise ValueError('student_id is required')

        query = {'student_id': student_id}

        if course_id:
            # Find activity IDs for the course
            with get_db_connection() as client:
                db = client['comp5241_g10']
                activities = list(db.learning_activities.find({'course_id': course_id}, {'_id': 1}))
            activity_ids = [str(a['_id']) for a in activities]
            if activity_ids:
                query['activity_id'] = {'$in': activity_ids}
            else:
                return []

        with get_db_connection() as client:
            db = client['comp5241_g10']
            progresses = list(db.activity_progress.find(query).sort('last_accessed', -1))
        return progresses

    @staticmethod
    def get_submissions_for_grading(teacher_id: str, course_id: Optional[str] = None) -> Any:
        """Return submissions in status 'submitted' for activities created by teacher_id.

        If course_id provided, limit to that course.
        """
        if not teacher_id:
            raise ValueError('teacher_id is required')

        # Find activities created by this teacher
        activity_query = {'created_by': teacher_id}
        if course_id:
            activity_query['course_id'] = course_id

        with get_db_connection() as client:
            db = client['comp5241_g10']
            activities = list(db.learning_activities.find(activity_query, {'_id': 1}))
        activity_ids = [str(a['_id']) for a in activities]

        if not activity_ids:
            return []

        with get_db_connection() as client:
            db = client['comp5241_g10']
            submissions = list(db.activity_submissions.find({
                'activity_id': {'$in': activity_ids},
                'status': 'submitted'
            }).sort('submitted_at', 1))
        return submissions

    @staticmethod
    def get_submissions_for_activity(activity_id: str, teacher_id: Optional[str] = None) -> Any:
        """Return submissions for a specific activity. If teacher_id provided,
        you may enforce teacher ownership in the route using the activity record.
        """
        if not activity_id:
            raise ValueError('activity_id is required')

        with get_db_connection() as client:
            db = client['comp5241_g10']
            submissions = list(db.activity_submissions.find({
                'activity_id': str(activity_id)
            }).sort('submitted_at', 1))
        return submissions
