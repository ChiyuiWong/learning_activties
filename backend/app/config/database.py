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
    
    # Try to use real MongoDB first
    try:
        # Check if MongoDB is available by attempting a quick connection
        client = pymongo.MongoClient(**mongodb_settings, serverSelectionTimeoutMS=2000)
        # Test connection with a lightweight command
        client.admin.command('ismaster')
        print("✅ Connected to real MongoDB server")
        app.db_client = client
        app.db = app.db_client[app.config.get('MONGODB_DB', 'comp5241_g10')]
        app.using_mongomock = False
    except Exception as e:
        # MongoDB is not available, use mongomock for testing/development
        if mongomock:
            print(f"⚠️ MongoDB not available ({e}). Using mongomock for testing.")
            app.db_client = mongomock.MongoClient()
            app.db = app.db_client[app.config.get('MONGODB_DB', 'comp5241_g10_test')]
            app.using_mongomock = True
        else:
            print("❌ MongoDB not available and mongomock is not installed.")
            raise