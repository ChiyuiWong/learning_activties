# COMP5241 Group 10 - Course Management Module

## 📚 Overview

The Course Management Module is a comprehensive system designed for educational institutions to manage courses, students, materials, and announcements. This module provides both teacher and student interfaces with advanced features for course administration and learning management.

## 🌟 Key Features

### For Teachers (Instructors)
- **Course Creation & Management**: Create, edit, and publish courses with detailed information
- **Student Management**: 
  - Bulk import students via CSV
  - Export student lists
  - Track student progress and enrollment status
  - View detailed student analytics
- **Material Management**:
  - Upload course materials (PDFs, presentations, documents, images)
  - Organize materials by categories and modules
  - Control material availability with publish/unpublish and date restrictions
  - Track download statistics
- **Announcement System**:
  - Create course announcements with rich content
  - Schedule announcements for future publication
  - Pin urgent announcements
  - Set expiration dates
- **Teacher Dashboard**:
  - Real-time statistics on courses, students, and materials
  - Recent activity tracking
  - Import history with error reporting
  - Quick access to all course management tools

### For Students
- **Course Enrollment**: Browse and enroll in available courses
- **Material Access**: Download course materials with automatic tracking
- **Progress Tracking**: View personal progress across all enrolled courses
- **Announcements**: Receive course announcements and updates
- **Student Dashboard**: Overview of enrolled courses, progress, and recent announcements

### Advanced Features
- **Multi-University Support**: Support for cross-university course management
- **LMS Integration**: Framework for integrating with external LMS systems (Canvas, Moodle)
- **Role-Based Access Control**: Granular permissions for teachers vs students
- **Comprehensive Logging**: Audit trails for all actions and downloads
- **Responsive Design**: Mobile-friendly interface for all devices
- **Search & Filtering**: Advanced search and filtering capabilities
- **Pagination**: Efficient handling of large datasets

## 🏗️ Technical Architecture

### Backend Structure
```
backend/app/modules/courses/
├── __init__.py                 # Package initialization
├── models.py                  # Database models (MongoDB/MongoEngine)
├── routes.py                  # API endpoints and route handlers
└── services.py                # Business logic and data processing
```

### Frontend Structure
```
frontend/
├── teacher-dashboard.html     # Teacher dashboard interface
├── courses.html              # Course management interface
├── materials.html            # Teacher material management interface
├── student-dashboard.html    # Student dashboard interface
├── student-courses.html      # Student course browser interface
├── student-materials.html    # Student material download portal
├── sample_students.csv       # Sample student import data
├── sample_teachers.csv       # Sample teacher import data
└── static/js/
    ├── teacher-dashboard.js   # Teacher dashboard functionality
    ├── courses.js            # Course management JavaScript
    └── student-dashboard.js   # Student dashboard functionality
```

### Database Models

#### Core Models
- **Course**: Main course information with metadata, enrollment limits, and publishing status
- **CourseEnrollment**: Student enrollment records with progress tracking
- **CourseMaterial**: File uploads with access control and download tracking
- **CourseAnnouncement**: Course announcements with scheduling and priority
- **CourseModule**: Course content organization (future expansion)

#### Import/Export Models
- **StudentImportLog**: Tracks bulk import operations with statistics
- **ImportError**: Detailed error logging for failed imports
- **MaterialDownloadLog**: Tracks all material downloads for analytics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB 4.4+
- Flask 2.0+
- MongoEngine
- Flask-JWT-Extended
- Bootstrap 5.3+

### Development Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/COMP5241-2526Sem1/groupproject-team_10.git
   cd groupproject-team_10
   ```

2. **Install Dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Copy environment template
   cp backend/env.example backend/.env
   
   # Edit configuration
   nano backend/.env
   ```

4. **Initialize Database**
   ```bash
   python backend/database_connection/init_db.py
   ```

5. **Start Development Server**
   ```bash
   python backend/app.py
   ```

### Production Deployment

#### Method 1: Production Server Setup

1. **Server Preparation**
   ```bash
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   
   # Install Python and dependencies
   sudo apt install python3.8 python3-pip mongodb nginx -y
   ```

2. **MongoDB Configuration**
   ```bash
   # Start MongoDB service
   sudo systemctl start mongod
   sudo systemctl enable mongod
   
   # Secure MongoDB installation
   sudo mongo --eval "db.adminCommand({createUser: {
     user: 'admin',
     pwd: 'secure_password',
     roles: ['userAdminAnyDatabase']
   }})"
   ```

3. **Application Setup**
   ```bash
   # Create application directory
   sudo mkdir -p /opt/course-management
   cd /opt/course-management
   
   # Clone and setup application
   sudo git clone https://github.com/COMP5241-2526Sem1/groupproject-team_10.git .
   sudo pip3 install -r backend/requirements.txt
   
   # Configure production environment
   sudo cp backend/env.example backend/.env
   sudo nano backend/.env  # Set production values
   ```

4. **Production Configuration**
   ```bash
   # backend/.env production settings
   FLASK_ENV=production
   DEBUG=False
   MONGODB_DB=comp5241_production
   MONGODB_HOST=localhost
   MONGODB_PORT=27017
   MONGODB_USERNAME=course_user
   MONGODB_PASSWORD=secure_db_password
   SECRET_KEY=production_secret_key_here
   JWT_SECRET_KEY=production_jwt_secret_here
   MAX_CONTENT_LENGTH=52428800
   UPLOAD_FOLDER=/opt/course-management/uploads/courses
   ```

5. **Initialize Production Database**
   ```bash
   cd /opt/course-management
   python3 backend/database_connection/init_db.py
   ```

6. **Start Production Server**
   ```bash
   # Using Gunicorn (recommended)
   pip3 install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
   
   # Or using Flask directly (development only)
   python3 backend/app.py
   ```

#### Method 2: Docker Deployment

1. **Create Dockerfile**
   ```dockerfile
   FROM python:3.8-slim
   
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 5000
   
   CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
   ```

2. **Docker Compose Setup**
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "5000:5000"
       environment:
         - MONGODB_HOST=mongodb
       depends_on:
         - mongodb
     
     mongodb:
       image: mongo:4.4
       ports:
         - "27017:27017"
       volumes:
         - mongodb_data:/data/db
   
   volumes:
     mongodb_data:
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose up -d
   ```

### First Time Setup

1. **Access the Application**
   - Development: http://localhost:5000
   - Production: https://your-domain.com

2. **Create Admin Account**
   ```bash
   # Register first admin user via API
   curl -X POST http://localhost:5000/api/security/register \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "email": "admin@university.edu",
       "password": "secure_password",
       "role": "teacher",
       "university": "PolyU"
     }'
   ```

3. **Login and Setup**
   - Login with admin credentials
   - Access Teacher Dashboard: `/teacher-dashboard`
   - Create your first course
   - Configure system settings

4. **Import Initial Data**
   - Use CSV import for bulk student enrollment
   - Upload course materials
   - Create course announcements

## 📋 API Documentation

### Course Management Endpoints

#### Create Course
```http
POST /api/courses/
Content-Type: application/json
Authorization: JWT (teacher role required)

{
  "title": "Advanced Database Systems",
  "course_code": "COMP5241",
  "description": "Advanced topics in database systems",
  "category": "Computer Science",
  "difficulty_level": "advanced",
  "max_students": 50,
  "semester": "Fall 2025",
  "university": "PolyU",
  "is_published": true
}
```

#### Get Courses
```http
GET /api/courses/?page=1&per_page=20&category=Computer%20Science&search=database
Authorization: JWT
```

#### Import Students
```http
POST /api/courses/{course_id}/students/import
Content-Type: multipart/form-data
Authorization: JWT (teacher role required)

Form Data:
- file: CSV file with columns (student_id, student_name, email, university, external_id)
```

#### Upload Material
```http
POST /api/courses/{course_id}/materials
Content-Type: multipart/form-data
Authorization: JWT (teacher role required)

Form Data:
- file: Material file (PDF, PPTX, DOCX, etc.)
- title: Material title
- description: Material description
- category: lecture|assignment|reading|media|other
- is_published: true|false
```

### Student Endpoints

#### Enroll in Course
```http
POST /api/courses/{course_id}/enroll
Authorization: JWT (student role)
```

#### Download Material
```http
GET /api/courses/materials/{material_id}/download
Authorization: JWT
```

### Response Format
All API responses follow this format:
```json
{
  "success": true|false,
  "data": {...},          // On success
  "error": "Error message", // On failure
  "pagination": {...}     // For paginated results
}
```

## 📊 CSV Import Format

### Student Import CSV
```csv
student_id,student_name,email,university,external_id
STU001,John Doe,john.doe@student.edu,PolyU,CANVAS_123
STU002,Jane Smith,jane.smith@student.edu,HKU,CANVAS_124
STU003,Mike Johnson,mike.johnson@student.edu,PolyU,MOODLE_456
```

**Required Fields**: `student_id`, `student_name`  
**Optional Fields**: `email`, `university`, `external_id`

**Sample File Available**: `frontend/sample_students.csv` - Ready-to-use sample data for testing

### Teacher Import CSV
```csv
teacher_id,teacher_name,email,department,specialization
T001,Dr. John Smith,john.smith@university.edu,Computer Science,Database Systems
T002,Prof. Jane Doe,jane.doe@university.edu,Information Technology,Web Development
T003,Dr. Alice Johnson,alice.johnson@university.edu,Computer Science,Machine Learning
```

**Required Fields**: `teacher_id`, `teacher_name`  
**Optional Fields**: `email`, `department`, `specialization`

**Sample File Available**: `frontend/sample_teachers.csv` - Ready-to-use sample data for testing

### Import Results
The system provides detailed import results:
- Total records processed
- Successful imports
- Failed imports (with error details)
- Duplicate records (automatically skipped)
- Error report export (CSV format)

## 🔒 Security Features

### Access Control
- **Role-Based Permissions**: Teachers and students have different access levels
- **Course Ownership**: Teachers can only manage their own courses
- **Material Access**: Students can only access published materials
- **JWT Authentication**: Secure token-based authentication

### File Security
- **File Type Validation**: Only approved file types allowed
- **File Size Limits**: Maximum 50MB per file
- **Secure File Storage**: Files stored outside web root
- **Download Logging**: All downloads tracked for audit

### Data Protection
- **Input Validation**: All inputs validated and sanitized
- **SQL Injection Prevention**: Using MongoEngine ORM
- **XSS Protection**: Output encoding and CSP headers
- **CSRF Protection**: CSRF tokens for state-changing operations

## 🧪 Testing

### Pre-Test Setup

1. **Environment Setup**
   ```bash
   # Ensure test dependencies are installed
   pip install pytest pytest-flask pytest-mock
   
   # Set test environment
   export FLASK_ENV=testing
   export MONGODB_DB=comp5241_test
   ```

2. **Test Database Setup**
   ```bash
   # Initialize test database
   python backend/database_connection/init_db.py --test
   ```

### Running Tests

#### Unit Tests
```bash
# Run all course unit tests
python -m pytest backend/tests/test_courses.py -v

# Run specific test class
python -m pytest backend/tests/test_courses.py::TestCourseManagement -v

# Run with coverage report
python -m pytest backend/tests/test_courses.py --cov=backend/app/modules/courses --cov-report=html
```

#### Integration Tests
```bash
# Run all integration tests
python -m pytest backend/tests/test_courses_integration.py -v

# Run specific integration test
python -m pytest backend/tests/test_courses_integration.py::TestCourseAPIEndpoints -v
```

#### Complete Test Suite
```bash
# Run all course-related tests
python -m pytest backend/tests/test_courses*.py -v

# Run all tests with detailed output
python -m pytest backend/tests/ -v --tb=short

# Run tests in parallel (faster)
python -m pytest backend/tests/ -n auto
```

#### System-wide Tests
```bash
# Test all modules
python -m pytest backend/tests/ -v

# Health check tests
python -m pytest backend/tests/test_health.py -v

# Security tests
python -m pytest backend/tests/test_security.py -v
```

### Manual Testing Procedures

#### API Testing with cURL

1. **Authentication Test**
   ```bash
   # Login to get JWT token
   TOKEN=$(curl -s -X POST http://localhost:5000/api/security/login \
     -H "Content-Type: application/json" \
     -d '{"username":"teacher1","password":"password123"}' \
     | jq -r '.access_token')
   
   echo "Token: $TOKEN"
   ```

2. **Course Management Tests**
   ```bash
   # Create course
   curl -X POST http://localhost:5000/api/courses/ \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Course",
       "course_code": "TEST101",
       "description": "Test course description",
       "category": "Computer Science",
       "max_students": 30
     }'
   
   # Get courses
   curl -X GET "http://localhost:5000/api/courses/" \
     -H "Authorization: Bearer $TOKEN"
   
   # Get specific course
   COURSE_ID="your_course_id_here"
   curl -X GET "http://localhost:5000/api/courses/$COURSE_ID" \
     -H "Authorization: Bearer $TOKEN"
   ```

3. **File Upload Tests**
   ```bash
   # Test material upload
   curl -X POST "http://localhost:5000/api/courses/$COURSE_ID/materials" \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@test_material.pdf" \
     -F "title=Test Material" \
     -F "category=lecture" \
     -F "is_published=true"
   
   # Test CSV import
   curl -X POST "http://localhost:5000/api/courses/$COURSE_ID/students/import" \
     -H "Authorization: Bearer $TOKEN" \
     -F "file=@test_students.csv"
   ```

#### Frontend Testing

1. **Start Test Server**
   ```bash
   # Start standalone test server for frontend
   python backend/tests/test_server.py
   # Access: http://localhost:5001
   ```

2. **Manual UI Tests**
   - Teacher Dashboard: http://localhost:5001/teacher-dashboard.html
   - Course Management: http://localhost:5001/courses.html
   - Student Dashboard: http://localhost:5001/student-dashboard.html

3. **Browser Testing Checklist**
   - [ ] Login functionality
   - [ ] Course creation and editing
   - [ ] Student import/export
   - [ ] Material upload/download
   - [ ] Announcement management
   - [ ] Dashboard statistics
   - [ ] Responsive design on mobile
   - [ ] Error handling and validation

### Performance Testing

1. **Load Testing with Apache Bench**
   ```bash
   # Test course listing endpoint
   ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/courses/
   
   # Test file download
   ab -n 100 -c 5 -H "Authorization: Bearer $TOKEN" \
     http://localhost:5000/api/courses/materials/MATERIAL_ID/download
   ```

2. **Database Performance**
   ```bash
   # MongoDB performance monitoring
   mongo --eval "db.runCommand({serverStatus: 1})"
   
   # Check query performance
   mongo comp5241_g10 --eval "db.courses.explain('executionStats').find({})"
   ```

### Test Coverage Analysis

```bash
# Generate coverage report
python -m pytest backend/tests/test_courses*.py \
  --cov=backend/app/modules/courses \
  --cov-report=html \
  --cov-report=term-missing

# View coverage report
open htmlcov/index.html
```

### Current Test Coverage
The test suite covers:
- ✅ **Course CRUD Operations** (16 tests)
  - Course creation, reading, updating, deletion
  - Validation and error handling
  - Access control and permissions

- ✅ **Student Management** (12 tests)
  - Enrollment and unenrollment
  - CSV import/export functionality
  - Progress tracking
  - Duplicate detection

- ✅ **Material Management** (8 tests)
  - File upload and validation
  - Download tracking
  - Access control
  - File type restrictions

- ✅ **Announcement System** (6 tests)
  - Creation and scheduling
  - Priority and expiration
  - Visibility controls

- ✅ **API Integration** (12 tests)
  - RESTful endpoints
  - Authentication flows
  - Error responses
  - Pagination

- ✅ **Dashboard & Analytics** (4 tests)
  - Statistics calculation
  - Activity tracking
  - Performance metrics

### Automated Testing (CI/CD)

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      mongodb:
        image: mongo:4.4
        ports:
          - 27017:27017
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    
    - name: Install dependencies
      run: pip install -r backend/requirements.txt
    
    - name: Run tests
      run: python -m pytest backend/tests/ -v --cov=backend/app
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

### Troubleshooting Tests

1. **Common Issues**
   ```bash
   # MongoDB connection issues
   sudo systemctl restart mongod
   
   # Clear test database
   mongo comp5241_test --eval "db.dropDatabase()"
   
   # Reset test environment
   export FLASK_ENV=testing
   python backend/database_connection/init_db.py --test
   ```

2. **Debug Test Failures**
   ```bash
   # Run with verbose output
   python -m pytest backend/tests/test_courses.py -v -s
   
   # Run specific failing test
   python -m pytest backend/tests/test_courses.py::TestCourseManagement::test_create_course -v -s
   
   # Use debugger
   python -m pytest backend/tests/test_courses.py --pdb
   ```

### Test Data Management

1. **Mock Data Creation**
   ```python
   # Use test fixtures for consistent data
   @pytest.fixture
   def sample_course():
       return {
           'title': 'Test Course',
           'course_code': 'TEST101',
           'description': 'Test description',
           'category': 'Computer Science',
           'max_students': 30
       }
   ```

2. **Test Database Cleanup**
   ```python
   # Automatic cleanup after each test
   @pytest.fixture(autouse=True)
   def clean_db():
       yield
       # Cleanup code here
       Course.objects.delete()
       CourseEnrollment.objects.delete()
   ```

## 📱 User Interface

### Teacher Dashboard Features
- **Statistics Cards**: Course count, student count, materials, downloads
- **Course Overview**: Quick access to all courses with status indicators
- **Recent Activity**: Real-time feed of enrollments and downloads
- **Import History**: Track all student import operations
- **Quick Actions**: One-click access to common tasks

### Course Management Interface
- **Advanced Filtering**: Search by title, category, semester, status
- **Bulk Operations**: Multiple course selection and actions
- **Detailed Course View**: Tabbed interface for overview, students, materials, announcements
- **Student Management**: Enrollment tracking, progress monitoring, bulk import
- **Material Organization**: Category-based organization with access control

### Student Interface
- **Clean Dashboard**: Focus on enrolled courses and progress
- **Material Browser**: Easy access to course materials with download tracking
- **Announcement Feed**: Chronological list of course announcements
- **Progress Tracking**: Visual progress bars and completion status

## 🔧 Configuration

### Environment Variables
```bash
# Database Configuration
MONGODB_DB=comp5241_g10
MONGODB_HOST=localhost
MONGODB_PORT=27017

# File Upload Configuration
MAX_CONTENT_LENGTH=52428800  # 50MB
UPLOAD_FOLDER=uploads/courses

# Security Configuration
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# Email Configuration (for notifications)
MAIL_SERVER=smtp.university.edu
MAIL_PORT=587
MAIL_USE_TLS=True
```

### Feature Flags
```python
# In config/config.py
FEATURES = {
    'BULK_IMPORT': True,
    'MATERIAL_UPLOAD': True,
    'LMS_INTEGRATION': False,  # Future feature
    'EMAIL_NOTIFICATIONS': False,  # Future feature
    'ADVANCED_ANALYTICS': False,  # Future feature
}
```

## 🚧 Future Enhancements

### Planned Features
1. **LMS Integration**: Full integration with Canvas, Moodle, Blackboard
2. **Advanced Analytics**: Detailed course and student analytics
3. **Email Notifications**: Automated email notifications for announcements
4. **Mobile App**: Native mobile applications for iOS and Android
5. **Video Content**: Support for video lectures and streaming
6. **Discussion Forums**: Course-specific discussion boards
7. **Gradebook**: Integrated grading and assessment tools
8. **Calendar Integration**: Course schedules and deadline management

### Technical Improvements
1. **Caching Layer**: Redis caching for improved performance
2. **File CDN**: Cloud-based file storage and delivery
3. **Real-time Updates**: WebSocket support for live updates
4. **API Versioning**: Versioned APIs for backward compatibility
5. **Microservices**: Break down into smaller, focused services
6. **GraphQL API**: Alternative to REST API for flexible queries

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Run the test suite: `python backend/tests/test_courses.py`
5. Commit your changes: `git commit -am 'Add new feature'`
6. Push to your branch: `git push origin feature/new-feature`
7. Create a Pull Request

### Code Standards
- Follow PEP 8 for Python code
- Use ESLint for JavaScript code
- Write comprehensive tests for new features
- Document all public APIs
- Use meaningful commit messages

### Team Members
- **Keith**: Course Management Module Lead
- **Charlie**: Learning Activities Integration
- **Sunny**: Security and Authentication
- **Ting**: AI/GenAI Integration

## 📄 License

This project is part of COMP5241 Group 10 coursework at The Hong Kong Polytechnic University.

## 📞 Support

For technical support or questions:
- Create an issue on the GitHub repository
- Contact the development team
- Refer to the test files for usage examples

---

**COMP5241 Group 10 Course Management Module** - Built with ❤️ for modern education