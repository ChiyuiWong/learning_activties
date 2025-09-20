"""
COMP5241 Group 10 - Security Module Services
Responsible: Sunny
"""
import base64

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from flask import current_app, request
from flask_jwt_extended import create_access_token
import bcrypt

from config.database import get_db_connection
from .models import User, UserSession, SecurityAuditLog
import pymongo
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class SecurityService:
    """Service class for security operations"""
    
    @staticmethod
    def authenticate_user(username, password):
        """Authenticate user credentials - to be implemented by Sunny"""
        try:
            db = get_db_connection()
            user_doc = db["users"].find_one({"username": username})
            if user_doc is None:
                return False
            cipher = Cipher(algorithms.AES(base64.b64decode(os.environ.get("PW_HASH_ENC_KEY"))), modes.CBC(user_doc["encrypted_pw_hash_iv"]))
            decryptor = cipher.decryptor()
            padded = decryptor.update(user_doc["encrypted_pw_hash"]) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            org_hashed_pw = unpadder.update(padded) + unpadder.finalize()
            hashed_pw = bcrypt.kdf(
                password=password.encode("utf-8"),
                salt=user_doc["pw_hash_salt"],
                desired_key_bytes=32,
                rounds=1000)
            return hashed_pw == org_hashed_pw
        except:
            return False

    @staticmethod
    def get_role(username, password):
        if not SecurityService.authenticate_user(username, password):
            return None
        # Authenticated section
        db = get_db_connection()
        user_doc = db["users"].find_one({"username": username})
        if user_doc is None:
            return None
        user_role = user_doc["role"]
        if user_role is None or user_role == "":
            return None
        if user_role not in ["student", "teacher", "admin"]:
            return None
        return user_role
    
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
