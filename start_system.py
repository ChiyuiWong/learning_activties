<<<<<<< Updated upstream
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
import argparse

def start_mongodb():
    """Check MongoDB Atlas connection"""
    print("✅ Using MongoDB Atlas - no local MongoDB needed")
    return True

def start_backend_server():
    """Start the Flask backend server"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    project_root = os.path.dirname(__file__)
    os.chdir(backend_dir)
    try:
        process = subprocess.Popen([sys.executable, 'run_server.py'], stdout=None, stderr=None)
        return process
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        return None
    
    print("🚀 Starting Flask backend server with uv...")
    try:
        # Use uv to run the Flask app
        return subprocess.Popen([
            'uv', 'run', 'python', 'app.py'
        ], cwd=backend_dir, env={**os.environ, 'PYTHONPATH': project_root})
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        print("💡 Make sure you have 'uv' installed: pip install uv")
        return None

def open_browser(page, port):
    """Open the browser after a delay"""
    base = f'http://localhost:{port}'
    url = f"{base}/{page.lstrip('/')}" if page else base
    print(f"🌐 Opening browser to {url}...")
    webbrowser.open(url)

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='Start LMS backend and optionally open a frontend page.')
    parser.add_argument('--page', default='login.html', help='Relative frontend page to open (e.g. polls_clean.html). Use "" to skip.')
    parser.add_argument('--no-browser', action='store_true', help='Do not automatically open a browser.')
    parser.add_argument('--port', type=int, default=int(os.environ.get('LMS_BACKEND_PORT', 5000)), help='Backend port to display/open (default 5000).')
    args = parser.parse_args()

    print("=" * 60)
    print("🎓 COMP5241 Group 10 - Learning Management System")
    print("=" * 60)
    print()
    
    # Start MongoDB first
    if not start_mongodb():
       print("❌ Failed to start MongoDB.")
    
    # Start backend server
    backend_process = start_backend_server()
    
    if backend_process:
        print("✅ Backend server started successfully!")
        print(f"📊 Backend API: http://localhost:{args.port}/api")
        print(f"🌐 Frontend App: http://localhost:{args.port}")
        if args.page:
            print(f"🔗 Auto-open Page: http://localhost:{args.port}/{args.page.lstrip('/')}")
        else:
            print("ℹ️ Browser auto-open disabled (empty page string).")
        print()
        
        # Open browser after 3 seconds
        if not args.no_browser and args.page:
            timer = Timer(3.0, open_browser, args=(args.page, args.port))
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
=======
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
import argparse

def start_mongodb():
    """Check MongoDB Atlas connection"""
    print("✅ Using MongoDB Atlas - no local MongoDB needed")
    return True

def start_backend_server():
    """Start the Flask backend server"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    project_root = os.path.dirname(__file__)
    
    print("🚀 Starting Flask backend server...")
    try:
        # 使用 run_test_server_only.py 启动服务器
        return subprocess.Popen([
            sys.executable, 'run_test_server_only.py'
        ], cwd=backend_dir, env={**os.environ, 'PYTHONPATH': project_root})
    except Exception as e:
        print(f"❌ Failed to start backend server: {e}")
        print("💡 请检查 Python 环境和依赖是否正确安装")
        return None

def open_browser(page, port):
    """Open the browser after a delay"""
    base = f'http://localhost:{port}'
    url = f"{base}/{page.lstrip('/')}" if page else base
    print(f"🌐 Opening browser to {url}...")
    webbrowser.open(url)

def main():
    """Main startup function"""
    parser = argparse.ArgumentParser(description='Start LMS backend and optionally open a frontend page.')
    parser.add_argument('--page', default='login.html', help='Relative frontend page to open (e.g. polls_clean.html). Use "" to skip.')
    parser.add_argument('--no-browser', action='store_true', help='Do not automatically open a browser.')
    parser.add_argument('--port', type=int, default=int(os.environ.get('LMS_BACKEND_PORT', 5000)), help='Backend port to display/open (default 5000).')
    args = parser.parse_args()

    print("=" * 60)
    print("🎓 COMP5241 Group 10 - Learning Management System")
    print("=" * 60)
    print()
    
    # Start MongoDB first
    if not start_mongodb():
       print("❌ Failed to start MongoDB.")
    
    # Start backend server
    backend_process = start_backend_server()
    
    if backend_process:
        print("✅ Backend server started successfully!")
        print(f"📊 Backend API: http://localhost:{args.port}/api")
        print(f"🌐 Frontend App: http://localhost:{args.port}")
        if args.page:
            print(f"🔗 Auto-open Page: http://localhost:{args.port}/{args.page.lstrip('/')}")
        else:
            print("ℹ️ Browser auto-open disabled (empty page string).")
        print()
        
        # Open browser after 3 seconds
        if not args.no_browser and args.page:
            timer = Timer(3.0, open_browser, args=(args.page, args.port))
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
>>>>>>> Stashed changes
    main()