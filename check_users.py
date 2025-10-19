#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pymongo import MongoClient
import json
from datetime import datetime

def check_users():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['comp5241_lms']
        users_collection = db['users']
        
        print("=== Checking MongoDB User Data ===")
        
        # Get all users
        users = list(users_collection.find({}))
        
        if not users:
            print("No users found in database")
            return
            
        print(f"Found {len(users)} users:")
        print()
        
        teachers = []
        students = []
        
        for user in users:
            user_info = {
                'username': user.get('username', 'N/A'),
                'email': user.get('email', 'N/A'),
                'role': user.get('role', 'N/A'),
                'name': user.get('name', user.get('full_name', 'N/A')),
                'created_at': user.get('created_at', 'N/A')
            }
            
            if user.get('role') == 'teacher':
                teachers.append(user_info)
            elif user.get('role') == 'student':
                students.append(user_info)
            else:
                print(f"Unknown role user: {user_info}")
        
        # Display teachers
        print("Teachers:")
        if teachers:
            for i, teacher in enumerate(teachers, 1):
                print(f"  {i}. Username: {teacher['username']}")
                print(f"     Name: {teacher['name']}")
                print(f"     Email: {teacher['email']}")
                print(f"     Created: {teacher['created_at']}")
                print()
        else:
            print("  No teachers found")
        
        # Display students
        print("Students:")
        if students:
            for i, student in enumerate(students, 1):
                print(f"  {i}. Username: {student['username']}")
                print(f"     Name: {student['name']}")
                print(f"     Email: {student['email']}")
                print(f"     Created: {student['created_at']}")
                print()
        else:
            print("  No students found")
            
        # Check for demo accounts
        print("Checking for demo accounts:")
        demo_accounts = []
        for user in users:
            username = user.get('username', '').lower()
            if any(demo_word in username for demo_word in ['demo', 'test', 'teacher1', 'student1', 'sample']):
                demo_accounts.append(user)
        
        if demo_accounts:
            print(f"Found {len(demo_accounts)} possible demo accounts:")
            for demo in demo_accounts:
                print(f"  - {demo.get('username')} ({demo.get('role', 'unknown')})")
        else:
            print("No obvious demo accounts found")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    check_users()
