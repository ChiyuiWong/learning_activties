"""
COMP5241 Group 10 - Security Module Services
Responsible: Sunny
"""
from flask import current_app, request
from flask_jwt_extended import create_access_token
import bcrypt
from .models import User, UserSession, SecurityAuditLog


class SecurityService:
    """Service class for security operations"""
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user credentials - to be implemented by Sunny"""
        # TODO: Implement user authentication logic
        pass
    
    @staticmethod
    def create_user(username, email, password, role='student'):
        """Create new user account - to be implemented by Sunny"""
        # TODO: Implement user creation logic
        pass
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt - to be implemented by Sunny"""
        # TODO: Implement password hashing
        pass
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against hash - to be implemented by Sunny"""
        # TODO: Implement password verification
        pass
    
    @staticmethod
    def create_session(user_id):
        """Create user session - to be implemented by Sunny"""
        # TODO: Implement session creation
        pass
    
    @staticmethod
    def invalidate_session(session_token):
        """Invalidate user session - to be implemented by Sunny"""
        # TODO: Implement session invalidation
        pass
    
    @staticmethod
    def log_security_event(user_id, action, details=None):
        """Log security event for audit - to be implemented by Sunny"""
        # TODO: Implement security logging
        pass
    
    @staticmethod
    def check_permissions(user, required_role):
        """Check if user has required permissions - to be implemented by Sunny"""
        # TODO: Implement permission checking
        pass
