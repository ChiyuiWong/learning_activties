"""
COMP5241 Group 10 - Database Configuration
"""
from mongoengine import connect, disconnect

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
    
    # Connect to MongoDB
    connect(**mongodb_settings)