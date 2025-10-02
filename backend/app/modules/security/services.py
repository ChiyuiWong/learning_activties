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
import datetime
import os
from dotenv import load_dotenv

from app.utils.action_logger import ActionLogger
from app.utils.interval_stats_counter import IntervalStatsCounter

load_dotenv()

class SecurityService:
    """Service class for security operations"""
    student_disallowed_name_list = ["professor", "prof.", "dr.", "teacher", "lecturer"]
    action_logger = ActionLogger("security")
    interval_stats_counter = IntervalStatsCounter("security")
    @staticmethod
    def authenticate_user(username, password, ip_address):
        """Authenticate user credentials"""
        try:
            with get_db_connection() as client:
                db = client['comp5241_g10']
                user_doc = db["users"].find_one({"username": username})
                if user_doc is None:
                    SecurityService.action_logger.log(username, ip_address, f"failed authentication with account not found.")
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
                SecurityService.action_logger.log(username, ip_address, f"{('successful' if hashed_pw == hashed_pw else 'failed')} authentication.")
                if hashed_pw == hashed_pw:
                    SecurityService.interval_stats_counter.count("authentication", "succeed")
                    return True
                else:
                    SecurityService.interval_stats_counter.count("authentication", "failed")
                    return True
        except Exception as e:
            SecurityService.action_logger.log(username, ip_address, f"failed authentication with {str(e)}.")
            return False

    @staticmethod
    def get_role(username, password, ip_address):
        if not SecurityService.authenticate_user(username, password, ip_address):
            return None
        # Authenticated section
        with get_db_connection() as client:
            db = client['comp5241_g10']
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
    def create_user(username, pw, activation_id, ip_address):
        """Create new user account"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
            new_user_doc = db["new_users"].find_one({"_id": activation_id})
            if new_user_doc is None:
                return "Activation ID not found."
            check_name_doc = db["users"].find_one({"username": username})
            if check_name_doc is not None:
                return "username already used by another user. Think of a new one."
            if new_user_doc["role"] == "student":
                for student_disallowed_name in SecurityService.student_disallowed_name_list:
                    if student_disallowed_name in username.lower():
                        return "Academic title disallowed because you are not a staff. If you have a valid degree and would want to include the title in your username, please contact the admin."
            # The user can create an account now
            salt = os.urandom(16)
            iv = os.urandom(16)
            hashed_pw = bcrypt.kdf(
                password=pw.encode("utf-8"),
                salt=salt,
                desired_key_bytes=32,
                rounds=1000)
            cipher = Cipher(algorithms.AES(base64.b64decode(os.environ.get("PW_HASH_ENC_KEY"))), modes.CBC(iv))
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            padded_plaintext = padder.update(hashed_pw) + padder.finalize()
            pw_ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
            db["users"].insert_one(
                {"_id": username,
                 "username": username,
                 "email": new_user_doc["email"],
                 "encrypted_pw_hash": pw_ciphertext,
                 "encrypted_pw_hash_iv": iv,
                 "pw_hash_salt": salt,
                 "first_name": new_user_doc["first_name"],
                 "last_name": new_user_doc["last_name"],
                 "role": new_user_doc["role"],
                 "is_active": True,
                 "is_verified": True,
                 "created_at": datetime.datetime.now(datetime.UTC),
                 })
            db["new_users"].delete_one({"_id": new_user_doc["_id"]})
            SecurityService.action_logger.log(username, ip_address, f"account created from activation code {new_user_doc["_id"]}")
        return "OK"
    
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
