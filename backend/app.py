"""
COMP5241 Group 10 - Main Application Entry Point
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create app without database initialization
app = create_app()

if __name__ == '__main__':
    try:
        # Try to import and initialize database
        from database_connection import init_db
        print("Initializing database connection...")
        try:
            client, db = init_db.init_database()
            app.db_client = client
            app.db = db
            print("Database initialized successfully.")
        except Exception as e:
            print(f"WARNING: Database initialization failed: {e}")
            print("Continuing in mock database mode.")
            app.db = {}  # Use a simple dict as a mock DB
            app.config['USING_MOCK_DB'] = True
    except Exception as e:
        print(f"WARNING: Could not load database module: {e}")
        print("Continuing without database support.")
        app.db = {}  # Use a simple dict as a mock DB
        app.config['USING_MOCK_DB'] = True
            
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0', port=5001)
