"""
Basic API test script for poll endpoints using requests.
Run: python test_poll_api.py
"""
import requests

API_URL = "http://localhost:5000/api/learning"
# Replace with valid JWT tokens for teacher and student
TEACHER_TOKEN = "<TEACHER_JWT_TOKEN>"
STUDENT_TOKEN = "<STUDENT_JWT_TOKEN>"

headers_teacher = {"Authorization": f"Bearer {TEACHER_TOKEN}"}
headers_student = {"Authorization": f"Bearer {STUDENT_TOKEN}"}

def test_create_poll():
    data = {
        "question": "What is your favorite color?",
        "options": ["Red", "Blue", "Green", "Yellow"],
        "course_id": "COURSE123"
    }
    r = requests.post(f"{API_URL}/polls", json=data, headers=headers_teacher)
    print("Create Poll:", r.status_code, r.json())
    return r.json().get("poll_id")

def test_vote_poll(poll_id):
    data = {"option_index": 1}  # Vote for "Blue"
    r = requests.post(f"{API_URL}/polls/{poll_id}/vote", json=data, headers=headers_student)
    print("Vote Poll:", r.status_code, r.json())

def test_get_results(poll_id):
    r = requests.get(f"{API_URL}/polls/{poll_id}/results", headers=headers_student)
    print("Poll Results:", r.status_code, r.json())

def main():
    poll_id = test_create_poll()
    if poll_id:
        test_vote_poll(poll_id)
        test_get_results(poll_id)

if __name__ == "__main__":
    main()
