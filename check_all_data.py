#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from pymongo import MongoClient
import json

def check_all_data():
    try:
        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        
        print("=== Checking All MongoDB Databases ===")
        
        # List all databases
        db_names = client.list_database_names()
        print(f"Available databases: {db_names}")
        print()
        
        # Check comp5241_g10 database
        db = client['comp5241_g10']
        collection_names = db.list_collection_names()
        print(f"Collections in comp5241_g10: {collection_names}")
        print()
        
        # Check each collection
        for collection_name in collection_names:
            collection = db[collection_name]
            count = collection.count_documents({})
            print(f"Collection '{collection_name}': {count} documents")
            
            if count > 0 and count <= 10:  # Show sample data for small collections
                print("  Sample documents:")
                for doc in collection.find().limit(3):
                    # Remove _id for cleaner output
                    if '_id' in doc:
                        del doc['_id']
                    print(f"    {doc}")
                print()
        
        # Check if there are any users in different possible collections
        possible_user_collections = ['users', 'user', 'accounts', 'auth_users', 'members']
        print("=== Checking for users in different collections ===")
        
        for coll_name in possible_user_collections:
            if coll_name in collection_names:
                coll = db[coll_name]
                users = list(coll.find({}))
                if users:
                    print(f"Found {len(users)} users in '{coll_name}' collection:")
                    for user in users:
                        print(f"  - Username: {user.get('username', 'N/A')}")
                        print(f"    Role: {user.get('role', 'N/A')}")
                        print(f"    Name: {user.get('name', user.get('full_name', 'N/A'))}")
                        print()
                else:
                    print(f"No users in '{coll_name}' collection")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    check_all_data()