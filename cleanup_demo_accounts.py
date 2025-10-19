#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pymongo import MongoClient

def cleanup_demo_accounts():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['comp5241_g10']
        users_collection = db['users']
        
        print("=== Cleaning Up Demo Accounts ===")
        
        # List current users
        all_users = list(users_collection.find({}, {'username': 1, 'role': 1, 'first_name': 1, 'last_name': 1}))
        print(f"Current users in database: {len(all_users)}")
        
        for user in all_users:
            print(f"  - {user['username']} ({user.get('role', 'unknown')}) - {user.get('first_name', '')} {user.get('last_name', '')}")
        
        # Demo accounts to remove
        demo_accounts = ['teacher1', 'admin1']  # Keep only real users
        
        removed_count = 0
        for demo_username in demo_accounts:
            result = users_collection.delete_one({'username': demo_username})
            if result.deleted_count > 0:
                print(f"Removed demo account: {demo_username}")
                removed_count += 1
            else:
                print(f"Demo account not found: {demo_username}")
        
        print(f"\nRemoved {removed_count} demo accounts")
        
        # Verify remaining users
        print("\n=== Remaining Users ===")
        remaining_users = list(users_collection.find({}, {'username': 1, 'role': 1, 'first_name': 1, 'last_name': 1}))
        
        teachers = [u for u in remaining_users if u.get('role') == 'teacher']
        students = [u for u in remaining_users if u.get('role') == 'student']
        
        print(f"Total remaining users: {len(remaining_users)}")
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
    cleanup_demo_accounts()









