# How to Run the Poll System

This guide provides step-by-step instructions for running the Poll System application.

## Prerequisites

- Python 3.11 or higher
- MongoDB 6.0 or higher

## Step 1: Install MongoDB

```bash
# For Ubuntu
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
```

## Step 2: Start MongoDB

```bash
# Create a directory for MongoDB data if it doesn't exist
mkdir -p /tmp/data/db

# Start MongoDB server
mongod --dbpath /tmp/data/db --bind_ip_all --port 27017
```

## Step 3: Install Python Dependencies

```bash
# Navigate to the backend directory
cd /workspaces/COMP5241_G10/backend

# Install required packages
pip install -r requirements.txt
```

## Step 4: Run the Flask Application

```bash
# Navigate to the backend directory
cd /workspaces/COMP5241_G10/backend

# Run the application
python app.py
```

The server will start on `http://localhost:5000`

## Step 5: Access the Poll System

Open your browser and navigate to:
- Main page: `http://localhost:5000`
- Poll system: `http://localhost:5000/polls`

## User Credentials for Testing

### Teachers
- Username: teacher1
- Password: password123

### Students
- Username: student1
- Password: password123

## API Endpoints

### Authentication
- `POST /api/security/login`: Login with username and password

### Poll Management
- `GET /api/learning/polls`: List all active polls
- `GET /api/learning/polls?course_id=COURSE123`: List polls for a specific course
- `POST /api/learning/polls`: Create a new poll (teacher only)
- `GET /api/learning/polls/<poll_id>`: Get a specific poll
- `POST /api/learning/polls/<poll_id>/vote`: Vote on a poll (student only)
- `GET /api/learning/polls/<poll_id>/results`: Get poll results
- `POST /api/learning/polls/<poll_id>/close`: Close a poll (teacher only)

## Troubleshooting

### MongoDB Connection Issues
If you encounter MongoDB connection issues, ensure:
1. MongoDB is running on port 27017
2. The database path exists and has proper permissions
3. No firewall is blocking the connection

### Application Errors
Check the Flask application logs for detailed error messages.