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
            'max_score': int(kwargs.get('max_score', 0)),
            'time_limit': int(kwargs.get('time_limit', 0)),
            'due_date': due_date,
            'is_active': bool(kwargs.get('is_active', True)),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'status': 'active'
        }

        with get_db_connection() as client:
            db = client['comp5241_g10']
            result = db.learning_activities.insert_one(activity_data)
        activity_data['_id'] = result.inserted_id
        return activity_data

    @staticmethod
    def get_activities(course_id: Optional[str] = None, created_by: Optional[str] = None,
                       is_active: bool = True, activity_type: Optional[str] = None) -> List:
        """Get learning activities filtered by parameters.

        Returns list of activity documents. Filter by:
        - course_id: activities for a specific course
        - created_by: activities created by a specific teacher
        - is_active: active/inactive activities
        - activity_type: filter by type (quiz, poll, etc.)
        """
        query = {}
        if course_id:
            query['course_id'] = str(course_id).strip()
        if created_by:
            query['created_by'] = str(created_by).strip()
        if is_active is not None:
            query['is_active'] = bool(is_active)
        if activity_type:
            query['activity_type'] = str(activity_type).strip()

        with get_db_connection() as client:
            db = client['comp5241_g10']
            activities = list(db.learning_activities.find(query))

        return activities

    @staticmethod
    def get_activity(activity_id: str) -> Optional[dict]:
        """Get a specific learning activity by ID.

        Returns the activity document or None if not found.
        """
        if not activity_id:
            raise ValueError('activity_id is required')

        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(activity_id, str):
                activity_id = ObjectId(activity_id)
        except Exception:
            # If ID is invalid, return None
            return None

        with get_db_connection() as client:
            db = client['comp5241_g10']
            activity = db.learning_activities.find_one({'_id': activity_id})

        return activity

    @staticmethod
    def update_activity(activity_id: str, **kwargs) -> Optional[dict]:
        """Update fields on an existing LearningActivity.

        Returns updated activity or None if not found.
        """
        if not activity_id:
            raise ValueError('activity_id is required')

        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(activity_id, str):
                activity_id = ObjectId(activity_id)
        except Exception:
            return None

        # Parse optional due_date
        due_date = kwargs.get('due_date')
        if isinstance(due_date, str):
            try:
                kwargs['due_date'] = datetime.fromisoformat(due_date)
            except Exception:
                raise ValueError('due_date must be a datetime or ISO date string')

        # Add updated_at timestamp
        kwargs['updated_at'] = datetime.utcnow()

        with get_db_connection() as client:
            db = client['comp5241_g10']
            result = db.learning_activities.update_one(
                {'_id': activity_id},
                {'$set': kwargs}
            )

        if result.matched_count == 0:
            return None

        with get_db_connection() as client:
            db = client['comp5241_g10']
            return db.learning_activities.find_one({'_id': activity_id})

    @staticmethod
    def delete_activity(activity_id: str, user_id: str, hard_delete: bool = False) -> bool:
        """Delete a learning activity.
        
        By default, performs a soft delete (sets status to 'deleted').
        If hard_delete=True, completely removes the activity and related data.
        Returns True on success, False if activity not found or user not authorized.
        
        Args:
            activity_id: ID of the activity to delete
            user_id: ID of the user requesting deletion (must be the creator)
            hard_delete: If True, permanently delete; otherwise mark as deleted
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        if not activity_id or not user_id:
            raise ValueError('activity_id and user_id are required')
            
        try:
            # Convert string ID to ObjectId if necessary
            if isinstance(activity_id, str):
                activity_id = ObjectId(activity_id)
        except Exception:
            return False
            
        # Get the activity to check ownership
        with get_db_connection() as client:
            db = client['comp5241_g10']
            activity = db.learning_activities.find_one({'_id': activity_id})
            
        # Check if activity exists and user is authorized
        if not activity:
            return False
            
        if activity.get('created_by') != user_id:
            # Only the creator can delete the activity
            return False
            
        activity_type = activity.get('activity_type')
        
        if hard_delete:
            # Perform hard delete (completely remove from database)
            with get_db_connection() as client:
                db = client['comp5241_g10']
                
                # Delete the activity document
                db.learning_activities.delete_one({'_id': activity_id})
                
                # Delete type-specific data
                if activity_type == 'quiz':
                    db.quizzes.delete_one({'activity_id': str(activity_id)})
                elif activity_type == 'poll':
                    db.polls.delete_one({'activity_id': str(activity_id)})
                elif activity_type == 'wordcloud':
                    db.wordclouds.delete_one({'activity_id': str(activity_id)})
                elif activity_type == 'shortanswer':
                    db.shortanswers.delete_one({'activity_id': str(activity_id)})
                elif activity_type == 'minigame':
                    db.minigames.delete_one({'activity_id': str(activity_id)})
                
                # Delete related data (submissions, progress, etc.)
                db.activity_progress.delete_many({'activity_id': str(activity_id)})
                db.activity_submissions.delete_many({'activity_id': str(activity_id)})
        else:
            # Perform soft delete (mark as deleted)
            with get_db_connection() as client:
                db = client['comp5241_g10']
                db.learning_activities.update_one(
                    {'_id': activity_id},
                    {'$set': {
                        'status': 'deleted',
                        'deleted_at': datetime.utcnow(),
                        'deleted_by': user_id
                    }}
                )
                
        return True

    @staticmethod
    def record_activity_progress(activity_id: str, student_id: str, progress_percentage: int, time_spent: int = 0) -> Any:
        """Record student's progress on an activity.

        Adds or updates progress record with time spent (in seconds) and completion percentage.
        Returns the progress record.
        """
        if not activity_id or not student_id:
            raise ValueError('activity_id and student_id are required')
        if progress_percentage < 0 or progress_percentage > 100:
            raise ValueError('progress_percentage must be between 0 and 100')

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