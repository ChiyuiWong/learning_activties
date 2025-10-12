import requests

try:
    print("Testing server health...")
    r = requests.get('http://localhost:5001/api/health')
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    print("\nCreating test poll...")
    poll_data = {
        "question": "Which teaching method do you prefer?",
        "options": ["Traditional lectures", "Interactive workshops", "Self-paced online learning"],
        "course_id": "COMP5241",
        "is_anonymous": True,
        "show_results": True,
        "status": "published",
        "visibility": "public",
        "created_by": "teacher1"
    }
    r = requests.post('http://localhost:5001/api/learning/polls/', json=poll_data)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
    
    print("\nGetting all polls...")
    r = requests.get('http://localhost:5001/api/learning/polls/')
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text}")
except Exception as e:
    print(f"Error: {e}")