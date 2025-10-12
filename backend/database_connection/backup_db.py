"""
COMP5241 Group 10 - Database Backup Script
"""
import pymongo
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def backup_database():
    """Create a backup of the MongoDB database"""
    try:
        # Connect to MongoDB
        mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/comp5241_g10')
        client = pymongo.MongoClient(mongodb_uri)
        
        # Get database name
        db_name = mongodb_uri.split('/')[-1] if '/' in mongodb_uri else 'comp5241_g10'
        db = client[db_name]
        
        # Create backup directory
        backup_dir = f"backups/{db_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        
        print(f"Creating backup of database: {db_name}")
        print(f"Backup location: {backup_dir}")
        
        # Get all collections
        collections = db.list_collection_names()
        
        for collection_name in collections:
            print(f"Backing up collection: {collection_name}")
            collection = db[collection_name]
            
            # Export collection to JSON
            documents = list(collection.find())
            
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            # Save to file
            backup_file = os.path.join(backup_dir, f"{collection_name}.json")
            with open(backup_file, 'w') as f:
                json.dump(documents, f, indent=2, default=str)
        
        # Create backup metadata
        metadata = {
            'database_name': db_name,
            'backup_timestamp': datetime.now().isoformat(),
            'collections': collections,
            'total_collections': len(collections)
        }
        
        metadata_file = os.path.join(backup_dir, 'backup_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"Backup completed successfully!")
        print(f"Total collections backed up: {len(collections)}")
        
    except Exception as e:
        print(f"Error creating backup: {e}")
        raise


if __name__ == "__main__":
    backup_database()
