"""
COMP5241 Group 10 - Learning Activities Module Models
Responsible: Charlie
"""
from mongoengine import Document, StringField, DateTimeField, ListField, DictField, IntField, BooleanField
from datetime import datetime


class LearningActivity(Document):
    """Model for learning activities"""
    title = StringField(required=True, max_length=200)
    description = StringField()
    activity_type = StringField(choices=['quiz', 'assignment', 'project', 'discussion'], required=True)
    course_id = StringField(required=True)
    created_by = StringField(required=True)  # teacher user_id
    instructions = StringField()
    max_score = IntField(default=100)
    time_limit = IntField()  # in minutes
    due_date = DateTimeField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'learning_activities',
        'indexes': ['course_id', 'activity_type', 'created_by', 'due_date']
    }


class ActivitySubmission(Document):
    """Model for activity submissions"""
    activity_id = StringField(required=True)
    student_id = StringField(required=True)
    submission_data = DictField()
    score = IntField()
    feedback = StringField()
    status = StringField(choices=['submitted', 'graded', 'returned'], default='submitted')
    submitted_at = DateTimeField(default=datetime.utcnow)
    graded_at = DateTimeField()
    graded_by = StringField()  # teacher user_id
    
    meta = {
        'collection': 'activity_submissions',
        'indexes': ['activity_id', 'student_id', 'status', 'submitted_at']
    }


class ActivityProgress(Document):
    """Model for tracking student progress on activities"""
    activity_id = StringField(required=True)
    student_id = StringField(required=True)
    progress_percentage = IntField(default=0)
    time_spent = IntField(default=0)  # in minutes
    last_accessed = DateTimeField(default=datetime.utcnow)
    is_completed = BooleanField(default=False)
    
    meta = {
        'collection': 'activity_progress',
        'indexes': ['activity_id', 'student_id', 'last_accessed']
    }
