"""
COMP5241 Group 10 - Application Configuration
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # MongoDB settings
    MONGODB_HOST = os.environ.get('MONGODB_HOST', 'localhost')
    MONGODB_PORT = int(os.environ.get('MONGODB_PORT', 27017))
    MONGODB_DB = os.environ.get('MONGODB_DB', 'comp5241_g10')
    # Add other MongoDB settings if needed
    # MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')
    # MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD')
    
    # CORS settings
    CORS_ORIGINS = ['http://localhost:3000', 'http://127.0.0.1:3000']