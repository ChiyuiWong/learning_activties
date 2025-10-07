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
    collections_names = db.list_collection_names()
    # Users collection indexes
    if "users" not in collections_names:
        db.create_collection(
            "users",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "_id",
                        "created_at",
                        "email",
                        "encrypted_pw_hash",
                        "first_name",
                        "is_active",
                        "is_verified",
                        "last_name",
                        "role",
                        "username"
                    ],
                    "properties": {
                        "_id": {
                            "bsonType": "string"
                        },
                        "created_at": {
                            "bsonType": "date"
                        },
                        "email": {
                            "bsonType": "string"
                        },
                        "encrypted_pw_hash": {
                            "bsonType": "binData",
                            "minLength": 48,
                            "maxLength": 48,
                        },
                        "encrypted_pw_hash_iv": {
                            "bsonType": "binData",
                            "minLength": 16,
                            "maxLength": 16
                        },
                        "first_name": {
                            "bsonType": "string"
                        },
                        "is_active": {
                            "bsonType": "bool"
                        },
                        "is_verified": {
                            "bsonType": "bool"
                        },
                        "last_name": {
                            "bsonType": "string"
                        },
                        "pw_hash_salt": {
                            "bsonType": "binData",
                            "minLength": 16,
                            "maxLength": 16
                        },
                        "role": {
                            "bsonType": "string",
                            "enum": ["student", "teacher", "admin"]
                        },
                        "username": {
                            "bsonType": "string"
                        }
                    }
                }
            }
        )
        db.users.create_index("username", unique=True)
        db.users.create_index("email", unique=True)
        db.users.create_index([("role", 1), ("is_active", 1)])

    # New users collection indexes
    if "new_users" not in collections_names:
        db.create_collection(
            "new_users",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "_id",
                        "email",
                        "first_name",
                        "last_name",
                        "role"
                    ],
                    "properties": {
                        "_id": {
                            "bsonType": "string",
                            "minLength": 32
                        },
                        "email": {
                            "bsonType": "string"
                        },
                        "first_name": {
                            "bsonType": "string"
                        },
                        "last_name": {
                            "bsonType": "string"
                        },
                        "role": {
                            "bsonType": "string",
                            "enum": ["student", "teacher"]
                        }
                    }
                }
            }
        )
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

    # Audit logs indexes
    if "action_log" not in collections_names:
        db.create_collection(
            "action_log",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["module", "encrypted_data", "encryption_iv", "created_at"],
                    "properties": {
                        "module": {
                            "bsonType": "string"

                        },
                        "encrypted_data": {
                            "bsonType": "binData"
                        },
                        "encryption_iv": {
                            "bsonType": "binData",
                            "minLength": 16,
                            "maxLength": 16
                        },
                        "created_at": {
                            "bsonType": "date",
                        }
                    }
                }
            }
        )
    if "interval_stats" not in collections_names:
        db.create_collection(
            "interval_stats",
            validator={
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": [
                        "_id",
                        "act",
                        "interval_num",
                        "module",
                        "val"
                    ],
                    "additionalProperties": False,
                    "properties": {
                        "_id": {
                            "bsonType": "objectId"
                        },
                        "act": {
                            "bsonType": "string"
                        },
                        "interval_num": {
                            "bsonType": "int",
                            "minimum": 1759837655
                        },
                        "module": {
                            "bsonType": "string"
                        },
                        "type": {
                            "bsonType": "string"
                        },
                        "val": {
                            "bsonType": ["double", "int"]
                        }
                    }
                }
            }
        )
    if "zip_pw" not in collections_names:
        db.create_collection("zip_pw",
                             validator={
                                 "$jsonSchema": {
                                     "bsonType": "object",
                                     "required": [
                                         "_id",
                                         "password"
                                     ],
                                     "properties": {
                                         "_id": {
                                             "bsonType": "string",
                                             "minLength": 64
                                         },
                                         "password": {
                                             "bsonType": "string",
                                             "minLength": 44
                                         }
                                     }
                                 }
                             })
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

    # Insert sample users (update if exists)
    db.users.replace_one({"_id": "admin1"}, sample_admin, upsert=True)
    db.users.replace_one({"_id": "teacher1"}, sample_teacher, upsert=True)

    print("Inserted sample data")
