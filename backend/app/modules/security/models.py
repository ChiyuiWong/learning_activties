"""
COMP5241 Group 10 - Security Module Models
Responsible: Sunny
"""
from mongoengine import Document, StringField, EmailField, DateTimeField, BooleanField, ListField
from datetime import datetime
import bcrypt


class User(Document):
    """User model for authentication and authorization"""
    username = StringField(required=True, unique=True, max_length=50)
    email = EmailField(required=True, unique=True)
    password_hash = StringField(required=True)
    first_name = StringField(max_length=50)
    last_name = StringField(max_length=50)
    role = StringField(choices=['student', 'teacher', 'admin'], default='student')
    is_active = BooleanField(default=True)
    is_verified = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    last_login = DateTimeField()
    
    meta = {
        'collection': 'users',
        'indexes': ['username', 'email', 'role']
    }
    
    def set_password(self, password):
        """Hash and set password"""
        # TODO: Implement password hashing - Sunny's responsibility
        pass
    
    def check_password(self, password):
        """Check if password is correct"""
        # TODO: Implement password verification - Sunny's responsibility
        pass


class UserSession(Document):
    """Model for tracking user sessions"""
    user_id = StringField(required=True)
    session_token = StringField(required=True, unique=True)
    ip_address = StringField()
    user_agent = StringField()
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)
    is_active = BooleanField(default=True)
    
    meta = {
        'collection': 'user_sessions',
        'indexes': ['user_id', 'session_token', 'expires_at']
    }


class SecurityAuditLog(Document):
    """Model for security audit logging"""
    user_id = StringField()
    action = StringField(required=True)
    ip_address = StringField()
    user_agent = StringField()
    details = StringField()
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'security_audit_logs',
        'indexes': ['user_id', 'action', 'timestamp']
    }
