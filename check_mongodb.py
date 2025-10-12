import pymongo
import json
from bson import ObjectId
from datetime import datetime

# MongoDB JSON Encoder to handle ObjectId and datetime
class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

try:
    # Connect to MongoDB
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['comp5241_g10']
    
    # Check available collections
    print("Available collections:", db.list_collection_names())
    
    # Check if we have polls collection
    if 'polls' in db.list_collection_names():
        print("\nPolls found. Listing all polls:")
        polls = list(db.polls.find())
        print(json.dumps(polls, indent=2, cls=MongoEncoder))
        print(f"Total polls: {len(polls)}")
    else:
        print("\nNo 'polls' collection found. Creating a test poll...")
        # Create a poll collection and add a test poll
        result = db.polls.insert_one({
            'question': 'Test Poll Created via Direct MongoDB Connection',
            'options': [
                {'text': 'Option A', 'votes': 0},
                {'text': 'Option B', 'votes': 0},
                {'text': 'Option C', 'votes': 0}
            ],
            'course_id': 'COMP5241',
            'created_by': 'teacher1',
            'is_active': True,
            'created_at': datetime.utcnow(),
            'expires_at': None
        })
        print(f"Created poll with ID: {result.inserted_id}")
    
    # Check if we have activities collection
    if 'learning_activities' in db.list_collection_names():
        print("\nLearning activities found. Listing all activities:")
        activities = list(db.learning_activities.find())
        print(json.dumps(activities, indent=2, cls=MongoEncoder))
        print(f"Total activities: {len(activities)}")
    
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")