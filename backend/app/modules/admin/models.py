"""
COMP5241 Group 10 - Admin Module Models
Responsible: Sunny
"""
from mongoengine import Document, StringField, DateTimeField, IntField, DictField
from datetime import datetime


class SystemConfiguration(Document):
    """Model for system configuration settings"""
    key = StringField(required=True, unique=True)
    value = StringField(required=True)
    description = StringField()
    updated_by = StringField(required=True)  # admin user_id
    updated_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'system_configurations',
        'indexes': ['key', 'updated_at']
    }


class AdminAction(Document):
    """Model for tracking admin actions"""
    admin_id = StringField(required=True)
    action_type = StringField(required=True)
    target_type = StringField()  # user, course, system, etc.
    target_id = StringField()
    description = StringField()
    metadata = DictField()
    performed_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'admin_actions',
        'indexes': ['admin_id', 'action_type', 'target_type', 'performed_at']
    }


class SystemStats(Document):
    """Model for storing system statistics snapshots"""
    date = DateTimeField(required=True)
    total_users = IntField(default=0)
    active_users = IntField(default=0)
    total_courses = IntField(default=0)
    active_courses = IntField(default=0)
    total_activities = IntField(default=0)
    server_metrics = DictField()
    
    meta = {
        'collection': 'system_stats',
        'indexes': ['date']
    }
