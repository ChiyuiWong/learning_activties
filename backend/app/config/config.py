"""
COMP5241 Group 10 - Application Configuration
"""
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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


class TestConfig(Config):
    """Testing configuration"""
    TESTING = True
    # Use a separate test DB by default
    MONGODB_DB = os.environ.get('MONGODB_TEST_DB', 'comp5241_g10_test')
    # If set to true, init_db will connect to mongomock for in-memory tests
    MONGODB_MOCK = True
    # Provide a deterministic encryption key for action logging during tests
    # (base64-encoded 32-byte key)
    ACTION_LOG_ENC_KEY = os.environ.get('ACTION_LOG_ENC_KEY', 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=')