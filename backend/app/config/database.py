"""
COMP5241 Group 10 - Database Configuration
"""
import pymongo
import os

try:
    import mongomock  # type: ignore
except Exception:
    mongomock = None

def init_db(app):
    """Initialize MongoDB connection"""
    # Get MongoDB settings from app config
    mongodb_settings = {
        'host': app.config.get('MONGODB_HOST', 'localhost'),
        'port': app.config.get('MONGODB_PORT', 27017),
        # Add username/password if needed
        # 'username': app.config.get('MONGODB_USERNAME'),
        # 'password': app.config.get('MONGODB_PASSWORD'),
    }
    
    # Connect to MongoDB or mongomock for tests
    if app.config.get('TESTING') and app.config.get('MONGODB_MOCK') and mongomock:
        # Use mongomock in-memory MongoDB
        app.db_client = mongomock.MongoClient()
        app.db = app.db_client[app.config.get('MONGODB_DB', 'comp5241_g10_test')]
    else:
        app.db_client = pymongo.MongoClient(**mongodb_settings)
        app.db = app.db_client[app.config.get('MONGODB_DB', 'comp5241_g10')]