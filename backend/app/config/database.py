"""
COMP5241 Group 10 - Database Configuration
"""
from mongoengine import connect, disconnect
import os

try:
    import mongomock  # type: ignore
except Exception:
    mongomock = None

def init_db(app):
    """Initialize MongoDB connection"""
    # Disconnect if already connected
    disconnect()
    
    # Get MongoDB settings from app config
    mongodb_settings = {
        'host': app.config.get('MONGODB_HOST', 'localhost'),
        'port': app.config.get('MONGODB_PORT', 27017),
        'db': app.config.get('MONGODB_DB', 'comp5241_g10'),
        # Add username/password if needed
        # 'username': app.config.get('MONGODB_USERNAME'),
        # 'password': app.config.get('MONGODB_PASSWORD'),
    }
    
    # Connect to MongoDB or mongomock for tests
    if app.config.get('TESTING') and app.config.get('MONGODB_MOCK') and mongomock:
        # Use mongomock in-memory MongoDB. Newer mongoengine versions require
        # passing mongo_client_class instead of the mongomock:// URI.
        connect(db=app.config.get('MONGODB_DB', 'comp5241_g10_test'), alias='default', mongo_client_class=mongomock.MongoClient)
    else:
        connect(**mongodb_settings)