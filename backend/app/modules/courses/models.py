"""
COMP5241 Group 10 - Courses Module Models
Responsible: Keith
"""
from mongoengine import Document, StringField, DateTimeField, ListField, BooleanField, IntField
from datetime import datetime


class Course(Document):
    """Model for courses"""
    title = StringField(required=True, max_length=200)
    description = StringField()
    course_code = StringField(required=True, unique=True, max_length=20)
    instructor_id = StringField(required=True)  # teacher user_id
    category = StringField(max_length=100)
    difficulty_level = StringField(choices=['beginner', 'intermediate', 'advanced'], default='beginner')
    max_students = IntField(default=100)
    is_active = BooleanField(default=True)
    is_published = BooleanField(default=False)
    start_date = DateTimeField()
    end_date = DateTimeField()
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'courses',
        'indexes': ['course_code', 'instructor_id', 'category', 'is_active']
    }


class CourseEnrollment(Document):
    """Model for course enrollments"""
    course_id = StringField(required=True)
    student_id = StringField(required=True)
    enrollment_date = DateTimeField(default=datetime.utcnow)
    completion_date = DateTimeField()
    progress_percentage = IntField(default=0)
    final_grade = StringField()
    status = StringField(choices=['enrolled', 'completed', 'dropped'], default='enrolled')
    
    meta = {
        'collection': 'course_enrollments',
        'indexes': ['course_id', 'student_id', 'status', 'enrollment_date']
    }


class CourseModule(Document):
    """Model for course modules/chapters"""
    course_id = StringField(required=True)
    title = StringField(required=True, max_length=200)
    description = StringField()
    order = IntField(required=True)
    content = StringField()
    is_published = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'course_modules',
        'indexes': ['course_id', 'order', 'is_published']
    }


class CourseAnnouncement(Document):
    """Model for course announcements"""
    course_id = StringField(required=True)
    title = StringField(required=True, max_length=200)
    content = StringField(required=True)
    created_by = StringField(required=True)  # instructor user_id
    created_at = DateTimeField(default=datetime.utcnow)
    is_pinned = BooleanField(default=False)
    
    meta = {
        'collection': 'course_announcements',
        'indexes': ['course_id', 'created_at', 'is_pinned']
    }
