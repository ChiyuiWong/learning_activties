#!/usr/bin/env python3
"""
COMP5241 Group 10 - Quick Start Script
Start the backend server and serve frontend files
"""
import os
import sys
import subprocess
import webbrowser
from threading import Timer

def start_mongodb():
    """Start MongoDB if not already running"""
    try:
        # Check if mongod is already running
        result = subprocess.run(['pgrep', 'mongod'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ MongoDB is already running")
            return True
            
        print("🗄️ Starting MongoDB...")
        
        # Create data directory
        mongodb_dir = '/tmp/mongodb/data'
        os.makedirs(mongodb_dir, exist_ok=True)
        
        # Start MongoDB
        cmd = ['mongod', '--dbpath', mongodb_dir, '--logpath', '/tmp/mongodb/mongo.log', '--fork']
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MongoDB started successfully")
            return True
        else:
            print(f"❌ Failed to start MongoDB: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting MongoDB: {e}")
        return False

def start_backend_server():
    """Start the Flask backend server"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    print("🚀 Starting Flask backend server...")
    try:
        # Try to run the Flask app
        return subprocess.Popen([
            sys.executable, 'app.py'
        ], cwd=backend_dir)
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None

def open_browser():
    """Open the browser after a delay"""
    print("🌐 Opening browser...")
    webbrowser.open('http://localhost:5000/login.html')

def main():
    """Main startup function"""
    print("=" * 60)
    print("🎓 COMP5241 Group 10 - Learning Management System")
    print("=" * 60)
    print()
    
    # Start MongoDB first
    if not start_mongodb():
        print("❌ Failed to start MongoDB. Exiting...")
        sys.exit(1)
    
    # Start backend server
    backend_process = start_backend_server()
    
    if backend_process:
        print("✅ Backend server started successfully!")
        print("📊 Backend API: http://localhost:5000/api")
        print("🌐 Frontend App: http://localhost:5000")
        print("🔐 Login Page: http://localhost:5000/login.html")
        print()
        
        # Open browser after 3 seconds
        timer = Timer(3.0, open_browser)
        timer.start()
        
        print("Demo Users:")
        print("👨‍🏫 Teachers: teacher1/password123, teacher2/password123")
        print("👨‍🎓 Students: student1/password123, student2/password123, student3/password123")
        print()
        print("Press Ctrl+C to stop the server...")
        
        try:
            # Wait for the backend process
            backend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down servers...")
            backend_process.terminate()
            backend_process.wait()
            print("✅ Servers stopped successfully!")
    else:
        print("❌ Failed to start servers. Please check the backend configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()