"""
COMP5241 Group 10 - Database Configuration and Connection
"""
import os

from mongoengine import connect, disconnect
import pymongo
from flask import current_app


def init_db(app):
    """Initialize MongoDB connection with Flask app"""
    mongodb_uri = app.config['MONGODB_SETTINGS']['host']
    
    try:
        # Initialize MongoEngine connection
        connect(host=mongodb_uri)
        app.logger.info(f"Connected to MongoDB: {mongodb_uri}")
    except Exception as e:
        app.logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def get_db_connection():
    """Get direct PyMongo connection for complex operations"""
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/comp5241_g10')
    client = pymongo.MongoClient(mongodb_uri)
    # Get database name from URI or use default
    return client


def close_db_connection():
    """Close MongoDB connection"""
    try:
        disconnect()
    except Exception as e:
        current_app.logger.error(f"Error closing database connection: {e}")
