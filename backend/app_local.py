"""
COMP5241 Group 10 - Local Development App
Runs the Flask app with mock database for testing
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('lms_app')
logger.setLevel(logging.INFO)

# Create app
app = create_app()

# Set mock database flag
app.config['USING_MOCK_DB'] = True
app.db = {}  # Use a simple dict as a mock DB

if __name__ == '__main__':
    print("Starting Flask app with mock database...")
    print("WARNING: AUTHENTICATION DISABLED - DEVELOPMENT MODE ONLY!")
    app.run(host='0.0.0.0', port=5001, debug=True)