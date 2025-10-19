#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pymongo import MongoClient
from datetime import datetime
import hashlib
import secrets

def create_real_users():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['comp5241_g10']
        users_collection = db['users']
        
        print("=== Creating Real User Accounts ===")
        
        # Define the real users from the login interface
        real_users = [
            # Teachers
            {
                'username': 'prof.smith',
                'email': 'prof.smith@comp5241.edu',
                'first_name': 'Prof.',
                'last_name': 'Smith',
                'role': 'teacher',
                'display_name': 'Prof. Smith',
                'department': 'Computer Science'
            },
            {
                'username': 'dr.johnson',
                'email': 'dr.johnson@comp5241.edu',
                'first_name': 'Dr.',
                'last_name': 'Johnson',
                'role': 'teacher',
                'display_name': 'Dr. Johnson',
                'department': 'Software Engineering'
            },
            # Students
            {
                'username': 'alice.wang',
                'email': 'alice.wang@student.comp5241.edu',
                'first_name': 'Alice',
                'last_name': 'Wang',
                'role': 'student',
                'display_name': 'Alice Wang',
                'student_id': 'S001'
            },
            {
                'username': 'bob.chen',
                'email': 'bob.chen@student.comp5241.edu',
                'first_name': 'Bob',
                'last_name': 'Chen',
                'role': 'student',
                'display_name': 'Bob Chen',
                'student_id': 'S002'
            },
            {
                'username': 'charlie.li',
                'email': 'charlie.li@student.comp5241.edu',
                'first_name': 'Charlie',
                'last_name': 'Li',
                'role': 'student',
                'display_name': 'Charlie Li',
                'student_id': 'S003'
            }
        ]
        
        # Use the same password hash as existing users for simplicity
        existing_user = users_collection.find_one({'username': 'teacher1'})
        if not existing_user:
            print("Error: Cannot find existing user to copy password hash")
            return
            
        # Copy password data from existing user
        password_data = {
            'encrypted_pw_hash': existing_user['encrypted_pw_hash'],
            'encrypted_pw_hash_iv': existing_user['encrypted_pw_hash_iv'],
            'pw_hash_salt': existing_user['pw_hash_salt']
        }
        
        created_count = 0
        updated_count = 0
        
        for user_data in real_users:
            # Check if user already exists
            existing = users_collection.find_one({'username': user_data['username']})
            
            # Prepare user document
            user_doc = {
                '_id': user_data['username'],  # Use username as string _id
                'username': user_data['username'],
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'role': user_data['role'],
                'is_active': True,
                'is_verified': True,
                'created_at': datetime.now(),
                **password_data
            }
            
            # Add additional fields
            if 'display_name' in user_data:
                user_doc['display_name'] = user_data['display_name']
            if 'department' in user_data:
                user_doc['department'] = user_data['department']
            if 'student_id' in user_data:
                user_doc['student_id'] = user_data['student_id']
            
            if existing:
                # Update existing user
                users_collection.update_one(
                    {'username': user_data['username']},
                    {'$set': user_doc}
                )
                print(f"Updated user: {user_data['username']} ({user_data['role']})")
                updated_count += 1
            else:
                # Create new user
                users_collection.insert_one(user_doc)
                print(f"Created user: {user_data['username']} ({user_data['role']})")
                created_count += 1
        
        print(f"\nSummary:")
        print(f"Created: {created_count} users")
        print(f"Updated: {updated_count} users")
        
        # Verify the users were created
        print("\n=== Verification ===")
        all_users = list(users_collection.find({}, {'username': 1, 'role': 1, 'first_name': 1, 'last_name': 1}))
        
        teachers = [u for u in all_users if u.get('role') == 'teacher']
        students = [u for u in all_users if u.get('role') == 'student']
        
        print(f"Total users in database: {len(all_users)}")
        print(f"Teachers: {len(teachers)}")
        for teacher in teachers:
            print(f"  - {teacher['username']} ({teacher.get('first_name', '')} {teacher.get('last_name', '')})")
        
        print(f"Students: {len(students)}")
        for student in students:
            print(f"  - {student['username']} ({student.get('first_name', '')} {student.get('last_name', '')})")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    create_real_users()