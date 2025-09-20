"""
COMP5241 Group 10 - Main Application Entry Point
"""
import sys
import os
from database_connection import init_db

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

if __name__ == '__main__':
    init_db.init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
