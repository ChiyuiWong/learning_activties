# Database Configuration and Setup

This directory contains database-related files for the COMP5241 Group 10 project.

## Files

- `init_db.py` - Database initialization script
- `backup_db.py` - Database backup script
- `restore_db.py` - Database restore script
- `mongo_queries.md` - Common MongoDB queries for the project

## Setup Instructions

1. **Install MongoDB** (if not already installed):
   ```bash
   # macOS
   brew install mongodb-community
   
   # Ubuntu
   sudo apt-get install mongodb
   
   # Windows - Download from MongoDB official website
   ```

2. **Start MongoDB service**:
   ```bash
   # macOS
   brew services start mongodb-community
   
   # Ubuntu
   sudo systemctl start mongod
   
   # Windows
   net start MongoDB
   ```

3. **Initialize the database**:
   ```bash
   cd database
   python init_db.py
   ```

## Database Schema

### Collections

- **users** - User accounts (students, teachers, admins)
- **courses** - Course information 
- **course_enrollments** - Student course enrollments
- **course_modules** - Course content modules
- **learning_activities** - Learning activities and assignments
- **activity_submissions** - Student submissions
- **activity_progress** - Student progress tracking
- **ai_generations** - AI generation history (GenAI module)
- **ai_analyses** - AI analysis results (GenAI module)
- **user_sessions** - User session management
- **security_audit_logs** - Security event logging
- **admin_actions** - Admin action tracking
- **system_configurations** - System settings

### Indexes

All collections have appropriate indexes for optimal query performance.

## Environment Variables

Required environment variables for database connection:

```bash
MONGODB_URI=mongodb://localhost:27017/comp5241_g10
```

## Team Responsibilities

- **Database Design**: All team members contribute to their module's schema
- **Security**: Sunny (user authentication, sessions, audit logs)
- **GenAI**: Ting (AI generations, analyses)
- **Learning Activities**: Charlie (activities, submissions, progress)
- **Courses**: Keith (courses, enrollments, modules)
- **Admin**: Sunny (admin actions, system config)
