"""
COMP5241 Group 10 - Admin Module Services
Responsible: Sunny
"""
import base64
import io
import json

import pymongo
import pyzipper
from config.database import get_db_connection
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pymongo.database import Database

from .models import SystemConfiguration, AdminAction, SystemStats
from ..security.models import User
import datetime
import os
from app.utils.action_logger import ActionLogger
from typing import List, Tuple


class AdminService:
    """Service class for admin operations"""
    action_logger = ActionLogger("admin")

    @staticmethod
    def get_all_users(admin_id):
        """Get all users in the system - to be implemented by Sunny"""
        # TODO: Implement user retrieval with admin permission check
        pass

    @staticmethod
    def update_user_by_admin(admin_id, user_id, update_data):
        """Update user by admin - to be implemented by Sunny"""
        # TODO: Implement user update with admin permission check
        pass

    @staticmethod
    def activate_deactivate_user(admin_id, user_id, is_active):
        """Activate or deactivate user - to be implemented by Sunny"""
        # TODO: Implement user activation/deactivation
        pass

    @staticmethod
    def get_system_configuration(key=None):
        """Get system configuration - to be implemented by Sunny"""
        # TODO: Implement configuration retrieval
        pass

    @staticmethod
    def update_system_configuration(admin_id, key, value, description=None):
        """Update system configuration - to be implemented by Sunny"""
        # TODO: Implement configuration update
        pass

    @staticmethod
    def log_admin_action(admin_id, action_type, target_type=None, target_id=None, description=None, metadata=None):
        """Log admin action - to be implemented by Sunny"""
        # TODO: Implement admin action logging
        pass

    @staticmethod
    def get_system_stats():
        """Get system statistics - to be implemented by Sunny"""
        # TODO: Implement system statistics calculation
        pass

    @staticmethod
    def new_users(users, admin_name, ip_address):
        """Initialize a batch of new users and return activation URL IDs"""
        with get_db_connection() as client:
            db = client['comp5241_g10']
            ret = []
            for user in users:
                if user["role"] == "admin":
                    ret.append([user["email"], "[FAILED] Generation failed: Admin can't create admin."])
                    continue
                if user["role"] not in ["teacher", "student"]:
                    ret.append([user["email"], "[FAILED] Generation failed: Incorrect role."])
                    continue
                check_email_doc = db["users"].find_one({"email": user["email"]})
                check_new_email_doc = db["new_users"].find_one({"email": user["email"]})
                if check_email_doc is not None or check_new_email_doc is not None:
                    ret.append(
                        [user["email"], "[FAILED] Generation failed: Account with this email address already exists."])
                    continue
                try:
                    url_id = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").replace("=", "$")
                    db["new_users"].insert_one({"_id": url_id, "email": user["email"], "first_name": user["first_name"],
                                                "last_name": user["last_name"], "role": user["role"]})
                    ret.append([user["email"], url_id])
                except Exception as e:
                    ret.append([user["email"], f"[FAILED] Generation failed: {str(e)}"])
            AdminService.action_logger.log(admin_name, ip_address,
                                           f"batch new users preparation with:\n{json.dumps(ret, indent=4)}")
            return ret

    @staticmethod
    def generate_audit_report(start_date=None, end_date=None):
        """Generate audit report - to be implemented by Sunny"""
        # TODO: Implement audit report generation
        pass

    @staticmethod
    def fetch_log(module: str = None, start_date: datetime = None, end_date: datetime = None, limit: int = 2048):
        query = {}
        if module is not None:
            query["module"] = module
        if start_date is not None or end_date is not None:
            query["created_at"] = {}
            if start_date is not None:
                query["created_at"]["$gte"] = start_date
            if end_date is not None:
                query["created_at"]["$lte"] = end_date
        docs = []
        with get_db_connection() as client:
            db: Database = client["comp5241_g10"]
            org_docs = db["action_log"].find(query).sort("created_at", -1).limit(limit)
            docs = list(org_docs)
            print(len(docs))
        decrypted_log = []
        print(len(docs))
        for doc in docs:
            cipher = Cipher(algorithms.AES(base64.b64decode(os.environ.get("ACTION_LOG_ENC_KEY"))),
                            modes.CBC(doc["encryption_iv"]))
            decryptor = cipher.decryptor()
            padded = decryptor.update(doc["encrypted_data"]) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded) + unpadder.finalize()
            plaintext = plaintext.decode("UTF-8")
            created_at: datetime = doc["created_at"]
            decrypted_log.append(f"{created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")} [{doc['module']}]: {plaintext}")
        decrypted_log = '\n'.join(decrypted_log)
        file, pw = AdminService.create_encrypted_zip([("lms.log", decrypted_log)])
        file_id = os.urandom(32).hex()
        AdminService.store_zip_pw(file_id, pw.decode("UTF-8"))
        return file, file_id

    @staticmethod
    def get_zip_pw(file_id):
        with get_db_connection() as client:
            db: Database = client["comp5241_g10"]
            pw = db["zip_pw"].find_one({"_id": file_id})["password"]
            db["zip_pw"].delete_one({"_id": file_id})
            db["zip_pw"].delete_many({"created_at": {}})
            AdminService.clear_old_zip_pw()
            return pw

    @staticmethod
    def store_zip_pw(file_id, pw):
        with get_db_connection() as client:
            db: Database = client["comp5241_g10"]
            db["zip_pw"].insert_one({"_id": file_id, "password": pw, "created_at": datetime.datetime.now(datetime.UTC)})
        AdminService.clear_old_zip_pw()

    @staticmethod
    def clear_old_zip_pw():
        with get_db_connection() as client:
            db: Database = client["comp5241_g10"]
            cutoff_time = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=10)
            db["zip_pw"].delete_many({"created_at": {"$lte": cutoff_time}})

    @staticmethod
    def create_encrypted_zip(files: List[Tuple[str, str]]):
        pw = base64.b64encode(os.urandom(32))
        zip_buffer = io.BytesIO()
        with pyzipper.AESZipFile(
                zip_buffer,
                'w',
                compression=pyzipper.ZIP_DEFLATED,
                encryption=pyzipper.WZ_AES
        ) as zipf:
            # Set password and encryption parameters
            zipf.setpassword(pw)
            zipf.setencryption(pyzipper.WZ_AES, nbits=256)
            for file in files:
                zipf.writestr(file[0], file[1])
        zip_buffer.seek(0)
        return zip_buffer.read(), pw

    @staticmethod
    def is_admin(user_id):
        """Check if user is admin - to be implemented by Sunny"""
        # TODO: Implement admin permission check
        pass
