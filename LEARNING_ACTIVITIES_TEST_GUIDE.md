# Learning Activities Testing Guide

This guide will help you test the Learning Activities module in our LMS system. As a teacher, you'll be able to create various types of learning activities and verify they work correctly.

## Prerequisites

1. Make sure MongoDB is running locally
2. Start the Flask backend server:
   ```
   cd backend
   python app.py
   ```
3. Access the frontend using a web browser at http://localhost:5001

## Test Scenario 1: Creating a Poll

### Steps:
1. Navigate to the dashboard at http://localhost:5001/index.html
2. Click on "Activities" in the navigation menu
3. Click the "Create New" button to open the activity creation view
4. Select "Create Poll" 
5. Fill in the required poll information:
   - Question: "What programming language do you prefer for web development?"
   - Add at least 3 options: "JavaScript", "Python", "PHP"
   - Enable "Anonymous Voting"
   - Enable "Show Results to Students"
   - Status: "Published"
6. Click "Create Poll" to submit the form
7. You should see a success notification and be redirected to My Activities view

### Verification:
- The poll should appear in the "My Activities" list
- The poll should be properly categorized under "Polls"
- Poll options should be visible
- There should be no JavaScript errors in the console

## Test Scenario 2: Creating a Word Cloud

### Steps:
1. Navigate to the dashboard
2. Click on "Activities" in the navigation menu
3. Click the "Create New" button
4. Select "Create Word Cloud"
5. Fill in the required information:
   - Question: "What words come to mind when you think of artificial intelligence?"
   - Add context and instructions
   - Set max words to 50
   - Status: "Published"
6. Click "Create Word Cloud" to submit

### Verification:
- The word cloud should appear in "My Activities"
- Word cloud settings should be stored correctly
- Status should show as "Published"

## Test Scenario 3: Student View of Activities

### Steps:
1. Log out if you're logged in as a teacher
2. Log in as a student (username: student1, password: password123)
3. Navigate to Activities
4. View the list of available activities

### Verification:
- Student should see all published activities
- Activities should be organized by type
- Student should not see "Create New" option

## Test Scenario 4: Responding to a Poll

### Steps:
1. As a student, navigate to Activities
2. Find the poll created earlier
3. Click to open it
4. Select an option
5. Submit your response

### Verification:
- Response should be recorded successfully
- Results should be displayed (if "Show Results" was enabled)
- Student should not be able to vote multiple times

## Test Scenario 5: Editing an Activity

### Steps:
1. Log in as a teacher
2. Navigate to "My Activities"
3. Find an existing activity and click the edit button
4. Make changes to the activity
5. Save the changes

### Verification:
- Changes should be saved correctly
- Updated activity should appear with the new information
- Database should reflect the changes

## Troubleshooting

If you encounter issues:

1. Check browser console for JavaScript errors
2. Verify the backend server is running
3. Check MongoDB connection
4. Verify CORS is properly configured
5. Confirm API endpoints are correct for each activity type:
   - Polls: `/api/learning/polls/`
   - Word Clouds: `/api/learning/wordclouds/`
   - Short Answers: `/api/learning/shortanswers/`
   - Quizzes: `/api/learning/quizzes/`
   - Mini Games: `/api/learning/minigames/`

## Learning Activities Data Model

### Poll Structure
```json
{
  "question": "What programming language do you prefer for web development?",
  "options": [
    {"text": "JavaScript", "votes": 0},
    {"text": "Python", "votes": 0},
    {"text": "PHP", "votes": 0}
  ],
  "course_id": "COMP5241",
  "created_by": "teacher1",
  "is_active": true,
  "is_anonymous": true,
  "show_results": true,
  "created_at": "2023-10-11T14:30:00.000Z",
  "expires_at": null
}
```

### Word Cloud Structure
```json
{
  "question": "What words come to mind when you think of artificial intelligence?",
  "instructions": "Enter up to 3 words that represent AI to you",
  "max_words": 50,
  "course_id": "COMP5241",
  "created_by": "teacher1",
  "is_active": true,
  "words": [],
  "created_at": "2023-10-11T14:45:00.000Z",
  "expires_at": null
}
```

## Future Improvements

1. Add real-time updates for live polls using WebSockets
2. Implement analytics dashboard for activity results
3. Add export functionality for activity data
4. Implement activity templates for quicker creation
5. Add grading capabilities for quiz and short answer activities