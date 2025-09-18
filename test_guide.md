# COMP5241 Group 10 Poll System - Testing Guide

This document outlines how to run the various tests for the Poll System application.

## Prerequisites

- MongoDB 6.0 or higher
- Python 3.11 or higher
- Node.js 16 or higher (for frontend tests)
- Required Python packages (installed via `pip install -r backend/requirements.txt`)
- Required Node packages (installed via `npm install`)

## Starting the MongoDB Server

Before running any tests, make sure MongoDB is running:

```bash
# Create a directory for MongoDB data if it doesn't exist
mkdir -p /tmp/data/db

# Start MongoDB server
mongod --dbpath /tmp/data/db --bind_ip_all --port 27017
```

## Backend Unit Tests

These tests validate the core functionality of the poll system:

```bash
# Navigate to the backend directory
cd /workspaces/COMP5241_G10/backend

# Run the unit tests
python -m pytest tests/test_poll_unit.py -v
```

## Backend Integration Tests

These tests verify that the complete system works properly end-to-end. The Flask application must be running:

```bash
# In Terminal 1: Start the Flask application
cd /workspaces/COMP5241_G10/backend
python app.py

# In Terminal 2: Run the integration tests
cd /workspaces/COMP5241_G10/backend
python -m pytest tests/test_poll_integration.py -v
```

## Frontend Tests with Playwright

These tests validate the frontend user interface:

```bash
# Make sure you're in the project root
cd /workspaces/COMP5241_G10

# Install required Node.js packages
npm install

# Run the tests
npm test
```

For a visual test runner:

```bash
npm run test:ui
```

## Manual Testing

For manual testing, follow these steps:

1. Start the MongoDB server:
```bash
mongod --dbpath /tmp/data/db --bind_ip_all --port 27017
```

2. Start the Flask application:
```bash
cd /workspaces/COMP5241_G10/backend
python app.py
```

3. Open your browser and navigate to:
   - Main page: `http://localhost:5000`
   - Poll system: `http://localhost:5000/polls`

4. Login with the provided credentials:
   - Teacher: `teacher1` / `password123`
   - Student: `student1` / `password123`

5. Test the following features:
   - Creating polls as a teacher
   - Viewing polls as a student
   - Voting on polls as a student
   - Viewing poll results
   - Closing polls as a teacher

## Test Coverage

The test suite covers the following aspects of the Poll System:

### Backend Unit Tests
- Poll creation validation
- Poll listing and filtering
- Poll voting logic
- Results calculation
- Poll state management (closing polls)
- Authorization checks

### Backend Integration Tests
- End-to-end workflow testing
- API endpoint testing
- Authentication integration
- Error handling

### Frontend Tests
- User login
- User interface rendering
- Poll creation workflow
- Poll voting workflow
- Results display
- Error handling and alerts

## Troubleshooting

If tests fail, check the following:

1. MongoDB is running and accessible on port 27017
2. The Flask application is running correctly
3. All dependencies are correctly installed
4. User accounts exist in the database

For specific test failures:
- Check the error messages in the test output
- Look at Flask server logs
- Check MongoDB data to see if records were properly created/updated