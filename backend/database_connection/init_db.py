"""
COMP5241 Group 10 - Database Initialization Script
"""
import base64

import pymongo
from datetime import datetime
import os
from dotenv import load_dotenv
from pymongo.errors import OperationFailure

load_dotenv()


def init_database():
    """Initialize MongoDB database with collections and indexes"""
    try:
        # Connect to MongoDB
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/comp5241_g10')
        client = pymongo.MongoClient(mongodb_uri)

        # Get database name from URI or use default
        db_name = 'comp5241_g10'
        db = client[db_name]

        # Create collections and indexes
        create_collections_and_indexes(db)

        # Insert sample data (optional)
        insert_sample_data(db)

        print("Database initialization completed successfully.")

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise


def create_collections_and_indexes(db):
    """Create collections and their indexes"""

    # Users collection indexes
    db.users.create_index("username", unique=True)
    db.users.create_index("email", unique=True)
    db.users.create_index([("role", 1), ("is_active", 1)])

    # New users collection indexes
    # Users collection indexes
    db.new_users.create_index("email", unique=True)
    db.new_users.create_index([("role", 1)])

    # Courses collection indexes
    db.courses.create_index("course_code", unique=True)
    db.courses.create_index([("instructor_id", 1), ("is_active", 1)])
    db.courses.create_index("category")

    # Course enrollments indexes
    db.course_enrollments.create_index([("course_id", 1), ("student_id", 1)], unique=True)
    db.course_enrollments.create_index("student_id")
    db.course_enrollments.create_index("status")

    # Learning activities indexes
    db.learning_activities.create_index([("course_id", 1), ("activity_type", 1)])
    db.learning_activities.create_index("due_date")

    # Activity submissions indexes
    db.activity_submissions.create_index([("activity_id", 1), ("student_id", 1)])
    db.activity_submissions.create_index("status")

    # User sessions indexes
    db.user_sessions.create_index("session_token", unique=True)
    db.user_sessions.create_index("expires_at", expireAfterSeconds=0)

    # Audit logs indexes
    db.security_audit_logs.create_index([("user_id", 1), ("timestamp", -1)])
    db.admin_actions.create_index([("admin_id", 1), ("performed_at", -1)])
    if 'action_log' not in db.list_collection_names():
        db.create_collection(
            'action_log',
            validator={
                '$jsonSchema': {
                    'bsonType': 'object',
                    'required': ['module', 'encrypted_data', 'encryption_iv', 'created_at'],
                    'properties': {
                        'module': {
                            'bsonType': 'string'

                        },
                        'encrypted_data': {
                            'bsonType': 'binData'
                        },
                        'encryption_iv': {
                            'bsonType': 'binData'
                        },
                        'created_at': {
                            'bsonType': 'date',
                        }
                    }
                }
            }
        )

    print("Created collections and indexes")


def insert_sample_data(db):
    """Insert sample data for development/testing"""

    # Sample admin user (password should be hashed in real implementation)
    sample_admin = {
        "_id": "admin1",
        "username": "admin1",
        "email": "admin@comp5241.edu",
        "encrypted_pw_hash": base64.b64decode("7d3lNVDtPbg3+L0SAoP+ZkcXxHZv5/dfcQJkx0+72bGqmZ0pyrPI+Xtncgn49DF1"),
        "encrypted_pw_hash_iv": base64.b64decode("LPA6e6FX2x8Qe2cEOBpneg=="),
        "pw_hash_salt": base64.b64decode("UTCB7gclTJoxeZPpMxv5CA=="),
        "first_name": "System",
        "last_name": "Administrator",
        "role": "admin",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow()
    }

    # Sample teacher user
    sample_teacher = {
        "_id": "teacher1",
        "username": "teacher1",
        "email": "teacher1@comp5241.edu",
        "encrypted_pw_hash": base64.b64decode("7d3lNVDtPbg3+L0SAoP+ZkcXxHZv5/dfcQJkx0+72bGqmZ0pyrPI+Xtncgn49DF1"),
        "encrypted_pw_hash_iv": base64.b64decode("LPA6e6FX2x8Qe2cEOBpneg=="),
        "pw_hash_salt": base64.b64decode("UTCB7gclTJoxeZPpMxv5CA=="),
        "first_name": "John",
        "last_name": "Doe",
        "role": "teacher",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow()
    }

    # Sample student user
    sample_student = {
        "_id": "student_001",
        "username": "student1",
        "email": "student1@comp5241.edu",
        "encrypted_pw_hash": "to_be_hashed",
        "first_name": "Jane",
        "last_name": "Smith",
        "role": "student",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow()
    }

    # Insert sample users (update if exists)
    db.users.replace_one({"_id": "admin1"}, sample_admin, upsert=True)
    db.users.replace_one({"_id": "teacher1"}, sample_teacher, upsert=True)
    db.users.replace_one({"_id": "student_001"}, sample_student, upsert=True)

    print("Inserted sample data")
