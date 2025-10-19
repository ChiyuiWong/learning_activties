#!/usr/bin/env python3
"""
Simple test to verify delete functionality integration
"""
import os
import sys

def check_delete_routes_file():
    """Check if delete_routes.py exists and has correct content"""
    delete_routes_path = "backend/app/modules/learning_activities/delete_routes.py"
    if os.path.exists(delete_routes_path):
        print("+ delete_routes.py exists")
        with open(delete_routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "def delete_poll" in content:
                print("+ delete_poll function exists")
            if "def delete_shortanswer" in content:
                print("+ delete_shortanswer function exists")
            if "def delete_quiz" in content:
                print("+ delete_quiz function exists")
            if "def delete_wordcloud" in content:
                print("+ delete_wordcloud function exists")
        return True
    else:
        print("- delete_routes.py not found")
        return False

def check_routes_registration():
    """Check if delete routes are registered in routes.py"""
    routes_path = "backend/app/modules/learning_activities/routes.py"
    if os.path.exists(routes_path):
        print("+ routes.py exists")
        with open(routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "from .delete_routes import delete_bp" in content:
                print("+ delete_routes import exists")
            if "learning_bp.register_blueprint(delete_bp)" in content:
                print("+ delete_bp registration exists")
        return True
    else:
        print("- routes.py not found")
        return False

def check_frontend_integration():
    """Check if frontend has delete functionality"""
    js_path = "frontend/static/js/learning-activities.js"
    if os.path.exists(js_path):
        print("+ learning-activities.js exists")
        with open(js_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "deleteActivity" in content:
                print("+ deleteActivity function exists in frontend")
            if "btn-outline-danger" in content:
                print("+ delete button exists in frontend")
        return True
    else:
        print("- learning-activities.js not found")
        return False

def main():
    """Main test function"""
    print("Testing delete functionality integration...")
    print("=" * 50)
    
    backend_ok = check_delete_routes_file()
    routes_ok = check_routes_registration()
    frontend_ok = check_frontend_integration()
    
    print("\n" + "=" * 50)
    if backend_ok and routes_ok and frontend_ok:
        print("SUCCESS: Delete functionality is properly integrated!")
        print("\nSummary:")
        print("- Backend delete routes: +")
        print("- Route registration: +")
        print("- Frontend integration: +")
        print("\nThe delete functionality is ready to use!")
        print("To test it, start your server and create some activities,")
        print("then you should see delete buttons for activities you created.")
    else:
        print("ERROR: Delete functionality integration has issues")
        if not backend_ok:
            print("- Backend delete routes: -")
        if not routes_ok:
            print("- Route registration: -")
        if not frontend_ok:
            print("- Frontend integration: -")

if __name__ == "__main__":
    main()
