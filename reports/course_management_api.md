# Course Management API Documentation

## Overview

This document provides comprehensive API documentation for the COMP5241 Group 10 Course Management Module. All endpoints require proper authentication unless otherwise specified.

## Authentication

The API uses JWT (JSON Web Token) authentication. Include the JWT token in the Authorization header:

```http
Authorization: Bearer <your-jwt-token>
```

### Role-Based Access Control

- **Teacher Role**: Full access to course management, student import, material upload
- **Student Role**: Limited access to enrollment, material downloads, viewing announcements
- **Admin Role**: Full system access (future implementation)

## Base URL

```
http://localhost:5000/api/courses
```

## Response Format

All API responses follow this standard format:

```json
{
  "success": true|false,
  "data": {...},              // Present on success
  "error": "Error message",   // Present on failure  
  "message": "Success message", // Optional
  "pagination": {             // Present for paginated responses
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## Endpoints

### 1. Course Management

#### 1.1 Get Courses

```http
GET /api/courses/
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)
- `search` (optional): Search in title, code, description
- `category` (optional): Filter by category
- `difficulty` (optional): Filter by difficulty level
- `status` (optional): Filter by status ('published', 'draft')
- `teacher_id` (optional): Filter by teacher (admin only)
- `university` (optional): Filter by university
- `semester` (optional): Filter by semester

**Example Request:**
```http
GET /api/courses/?page=1&per_page=10&category=Computer%20Science&search=database
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "60a7c8b5c9f4a12345678901",
      "title": "Advanced Database Systems",
      "course_code": "COMP5241",
      "description": "Advanced topics in database systems...",
      "category": "Computer Science",
      "difficulty_level": "advanced",
      "teacher_id": "60a7c8b5c9f4a12345678900",
      "teacher_name": "Dr. Smith",
      "max_students": 50,
      "enrolled_count": 23,
      "semester": "Fall 2025",
      "university": "PolyU",
      "is_published": true,
      "created_at": "2025-01-01T10:00:00Z",
      "updated_at": "2025-01-15T14:30:00Z",
      "enrollment_start_date": "2025-01-01T00:00:00Z",
      "enrollment_end_date": "2025-02-01T23:59:59Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

#### 1.2 Get Single Course

```http
GET /api/courses/{course_id}
```

**Path Parameters:**
- `course_id`: Course ID

**Example Response:**
```json
{
  "success": true,
  "data": {
    "id": "60a7c8b5c9f4a12345678901",
    "title": "Advanced Database Systems",
    "course_code": "COMP5241",
    "description": "Advanced topics in database systems including NoSQL, distributed databases, and big data processing.",
    "category": "Computer Science",
    "difficulty_level": "advanced",
    "teacher_id": "60a7c8b5c9f4a12345678900",
    "teacher_name": "Dr. Smith",
    "max_students": 50,
    "enrolled_count": 23,
    "semester": "Fall 2025",
    "university": "PolyU",
    "is_published": true,
    "created_at": "2025-01-01T10:00:00Z",
    "updated_at": "2025-01-15T14:30:00Z",
    "enrollment_start_date": "2025-01-01T00:00:00Z",
    "enrollment_end_date": "2025-02-01T23:59:59Z",
    "lms_integration": {
      "canvas_course_id": "12345",
      "moodle_course_id": null
    },
    "materials_count": 12,
    "announcements_count": 3
  }
}
```

#### 1.3 Create Course

```http
POST /api/courses/
```

**Required Role:** Teacher

**Request Body:**
```json
{
  "title": "Advanced Database Systems",
  "course_code": "COMP5241",
  "description": "Advanced topics in database systems",
  "category": "Computer Science",
  "difficulty_level": "advanced",
  "max_students": 50,
  "semester": "Fall 2025",
  "university": "PolyU",
  "is_published": true,
  "enrollment_start_date": "2025-01-01T00:00:00Z",
  "enrollment_end_date": "2025-02-01T23:59:59Z",
  "lms_integration": {
    "canvas_course_id": "12345"
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "message": "Course created successfully",
  "data": {
    "id": "60a7c8b5c9f4a12345678901",
    "title": "Advanced Database Systems",
    "course_code": "COMP5241"
  }
}
```

#### 1.4 Update Course

```http
PUT /api/courses/{course_id}
```

**Required Role:** Teacher (course owner)

**Request Body:** Same as create course (partial updates supported)

#### 1.5 Delete Course

```http
DELETE /api/courses/{course_id}
```

**Required Role:** Teacher (course owner)

**Example Response:**
```json
{
  "success": true,
  "message": "Course deleted successfully"
}
```

### 2. Student Management

#### 2.1 Get Course Students

```http
GET /api/courses/{course_id}/students
```

**Required Role:** Teacher (course owner) or Student (enrolled)

**Query Parameters:**
- `page`, `per_page`: Pagination
- `search`: Search by name or student ID
- `status`: Filter by enrollment status

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "60a7c8b5c9f4a12345678902",
      "student_id": "STU001",
      "student_name": "John Doe",
      "email": "john.doe@student.edu",
      "university": "PolyU",
      "enrolled_at": "2025-01-05T09:30:00Z",
      "progress": 75.5,
      "last_activity": "2025-01-15T16:45:00Z",
      "status": "active",
      "external_lms_id": "CANVAS_123"
    }
  ],
  "pagination": {...}
}
```

#### 2.2 Import Students (Bulk)

```http
POST /api/courses/{course_id}/students/import
```

**Required Role:** Teacher (course owner)

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: CSV file with student data

**CSV Format:**
```csv
student_id,student_name,email,university,external_id
STU001,John Doe,john.doe@student.edu,PolyU,CANVAS_123
STU002,Jane Smith,jane.smith@student.edu,HKU,CANVAS_124
```

**Sample File Available**: Use `frontend/sample_students.csv` for testing - contains ready-to-use sample data

**Example Response:**
```json
{
  "success": true,
  "message": "Student import completed",
  "data": {
    "import_id": "60a7c8b5c9f4a12345678903",
    "total_records": 100,
    "successful_imports": 95,
    "failed_imports": 3,
    "duplicate_records": 2,
    "error_report_url": "/api/courses/60a7c8b5c9f4a12345678901/students/import/60a7c8b5c9f4a12345678903/errors"
  }
}
```

#### 2.3 Export Students

```http
GET /api/courses/{course_id}/students/export
```

**Required Role:** Teacher (course owner)

**Response:** CSV file download

#### 2.4 Get Import History

```http
GET /api/courses/{course_id}/students/import/history
```

**Required Role:** Teacher (course owner)

#### 2.5 Enroll Student

```http
POST /api/courses/{course_id}/enroll
```

**Required Role:** Student

**Example Response:**
```json
{
  "success": true,
  "message": "Successfully enrolled in course",
  "data": {
    "enrollment_id": "60a7c8b5c9f4a12345678904",
    "course_title": "Advanced Database Systems",
    "enrolled_at": "2025-01-15T10:30:00Z"
  }
}
```

#### 2.6 Unenroll Student

```http
DELETE /api/courses/{course_id}/enroll
```

**Required Role:** Student (self) or Teacher (course owner)

### 3. Material Management

#### 3.1 Get Course Materials

```http
GET /api/courses/{course_id}/materials
```

**Query Parameters:**
- `category`: Filter by category (lecture, assignment, reading, media, other)
- `is_published`: Filter by published status
- `search`: Search in title and description

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "60a7c8b5c9f4a12345678905",
      "title": "Database Fundamentals - Week 1",
      "description": "Introduction to database concepts",
      "category": "lecture",
      "file_name": "week1_fundamentals.pdf",
      "file_size": 2048576,
      "file_type": "application/pdf",
      "is_published": true,
      "published_at": "2025-01-01T08:00:00Z",
      "available_from": "2025-01-01T00:00:00Z",
      "available_until": "2025-12-31T23:59:59Z",
      "download_count": 45,
      "uploaded_at": "2025-01-01T07:45:00Z",
      "module_id": null
    }
  ],
  "pagination": {...}
}
```

#### 3.2 Upload Material

```http
POST /api/courses/{course_id}/materials
```

**Required Role:** Teacher (course owner)

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file`: Material file (PDF, PPTX, DOCX, etc.)
- `title`: Material title
- `description`: Material description
- `category`: lecture|assignment|reading|media|other
- `is_published`: true|false
- `available_from`: ISO date string (optional)
- `available_until`: ISO date string (optional)

**Example Response:**
```json
{
  "success": true,
  "message": "Material uploaded successfully",
  "data": {
    "id": "60a7c8b5c9f4a12345678905",
    "title": "Database Fundamentals - Week 1",
    "file_name": "week1_fundamentals.pdf",
    "file_size": 2048576
  }
}
```

#### 3.3 Download Material

```http
GET /api/courses/materials/{material_id}/download
```

**Response:** File download (binary content)

**Headers:**
- `Content-Type`: Original file MIME type
- `Content-Disposition`: attachment; filename="original_filename.ext"

#### 3.4 Update Material

```http
PUT /api/courses/materials/{material_id}
```

**Required Role:** Teacher (course owner)

#### 3.5 Delete Material

```http
DELETE /api/courses/materials/{material_id}
```

**Required Role:** Teacher (course owner)

### 4. Announcement Management

#### 4.1 Get Course Announcements

```http
GET /api/courses/{course_id}/announcements
```

**Query Parameters:**
- `is_published`: Filter by published status
- `is_pinned`: Filter by pinned status
- `search`: Search in title and content

**Example Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "60a7c8b5c9f4a12345678906",
      "title": "Important: Midterm Exam Schedule",
      "content": "The midterm exam will be held on...",
      "is_published": true,
      "is_pinned": true,
      "is_urgent": false,
      "published_at": "2025-01-10T09:00:00Z",
      "expires_at": "2025-02-15T23:59:59Z",
      "created_at": "2025-01-10T08:45:00Z",
      "updated_at": "2025-01-10T09:00:00Z",
      "author_name": "Dr. Smith"
    }
  ],
  "pagination": {...}
}
```

#### 4.2 Create Announcement

```http
POST /api/courses/{course_id}/announcements
```

**Required Role:** Teacher (course owner)

**Request Body:**
```json
{
  "title": "Important: Midterm Exam Schedule",
  "content": "The midterm exam will be held on February 15th at 2:00 PM in Room A101.",
  "is_published": true,
  "is_pinned": true,
  "is_urgent": false,
  "published_at": "2025-01-10T09:00:00Z",
  "expires_at": "2025-02-15T23:59:59Z"
}
```

#### 4.3 Update Announcement

```http
PUT /api/courses/announcements/{announcement_id}
```

**Required Role:** Teacher (course owner)

#### 4.4 Delete Announcement

```http
DELETE /api/courses/announcements/{announcement_id}
```

**Required Role:** Teacher (course owner)

### 5. Dashboard and Statistics

#### 5.1 Teacher Dashboard Stats

```http
GET /api/courses/dashboard/teacher
```

**Required Role:** Teacher

**Example Response:**
```json
{
  "success": true,
  "data": {
    "courses_count": 5,
    "total_students": 250,
    "total_materials": 67,
    "total_downloads": 1543,
    "recent_enrollments": [
      {
        "student_name": "John Doe",
        "course_title": "Database Systems",
        "enrolled_at": "2025-01-15T10:30:00Z"
      }
    ],
    "recent_downloads": [
      {
        "student_name": "Jane Smith",
        "material_title": "Week 1 Lecture",
        "downloaded_at": "2025-01-15T14:20:00Z"
      }
    ],
    "import_history": [
      {
        "course_title": "Database Systems",
        "imported_at": "2025-01-10T09:00:00Z",
        "successful_count": 45,
        "failed_count": 2
      }
    ]
  }
}
```

#### 5.2 Student Dashboard Stats

```http
GET /api/courses/dashboard/student
```

**Required Role:** Student

**Example Response:**
```json
{
  "success": true,
  "data": {
    "enrolled_courses": [
      {
        "id": "60a7c8b5c9f4a12345678901",
        "title": "Advanced Database Systems",
        "course_code": "COMP5241",
        "teacher_name": "Dr. Smith",
        "progress": 75.5,
        "last_activity": "2025-01-15T16:45:00Z",
        "next_deadline": "2025-01-20T23:59:59Z"
      }
    ],
    "recent_announcements": [
      {
        "course_title": "Database Systems",
        "title": "Midterm Exam Schedule",
        "published_at": "2025-01-10T09:00:00Z",
        "is_urgent": false
      }
    ],
    "recent_materials": [
      {
        "course_title": "Database Systems",
        "title": "Week 3 Lecture Notes",
        "uploaded_at": "2025-01-12T10:00:00Z",
        "category": "lecture"
      }
    ]
  }
}
```

#### 5.3 Course Statistics

```http
GET /api/courses/{course_id}/stats
```

**Required Role:** Teacher (course owner)

**Example Response:**
```json
{
  "success": true,
  "data": {
    "enrollment_stats": {
      "total_enrolled": 45,
      "max_capacity": 50,
      "enrollment_rate": 90.0,
      "avg_progress": 68.5
    },
    "material_stats": {
      "total_materials": 12,
      "total_downloads": 324,
      "avg_downloads_per_material": 27.0,
      "most_popular_material": "Database Design Principles"
    },
    "activity_stats": {
      "daily_active_students": 23,
      "weekly_active_students": 41,
      "last_activity": "2025-01-15T18:30:00Z"
    },
    "enrollment_trends": [
      {"date": "2025-01-01", "count": 10},
      {"date": "2025-01-02", "count": 15},
      {"date": "2025-01-03", "count": 22}
    ]
  }
}
```

## Error Handling

### HTTP Status Codes

- `200`: Success
- `201`: Created successfully  
- `400`: Bad request (validation errors)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (insufficient permissions)
- `404`: Resource not found
- `409`: Conflict (duplicate resource)
- `413`: Payload too large (file upload limit)
- `422`: Unprocessable entity (validation errors)
- `500`: Internal server error

### Error Response Format

```json
{
  "success": false,
  "error": "Validation failed",
  "details": {
    "field_errors": {
      "title": ["Title is required"],
      "max_students": ["Must be a positive integer"]
    }
  }
}
```

### Common Error Messages

- `"Authentication required"`: Missing or invalid JWT token
- `"Insufficient permissions"`: User role doesn't allow this action
- `"Course not found"`: Invalid course ID
- `"Student already enrolled"`: Duplicate enrollment attempt
- `"Course capacity reached"`: Maximum students enrolled
- `"File too large"`: Upload exceeds size limit
- `"Invalid file type"`: Unsupported file format

## Rate Limiting

API endpoints are rate limited to prevent abuse:

- **General endpoints**: 1000 requests per hour per user
- **File upload endpoints**: 100 requests per hour per user
- **Bulk import endpoints**: 10 requests per hour per user

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests in window
- `X-RateLimit-Reset`: Unix timestamp when window resets

## Pagination

List endpoints support pagination with these parameters:

- `page`: Page number (1-based, default: 1)
- `per_page`: Items per page (default: 20, max: 100)

Pagination info is included in the response:

```json
{
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 156,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

## File Upload Requirements

### Supported File Types

**Course Materials:**
- Documents: PDF, DOC, DOCX, TXT, RTF
- Presentations: PPT, PPTX, ODP
- Spreadsheets: XLS, XLSX, ODS, CSV
- Images: JPG, JPEG, PNG, GIF, BMP, SVG
- Archives: ZIP, RAR, 7Z, TAR, GZ

**Import Files:**
- CSV files only for student imports

### File Size Limits

- **Individual files**: 50MB maximum
- **Batch uploads**: 200MB total per request

### Security Measures

- File type validation by content (not just extension)
- Virus scanning (future implementation)
- Safe file naming (special characters removed)
- Secure storage outside web root

## Webhooks (Future Feature)

Course management events can trigger webhooks for external integrations:

### Available Events

- `course.created`
- `course.updated` 
- `student.enrolled`
- `student.unenrolled`
- `material.uploaded`
- `material.downloaded`
- `announcement.published`

### Webhook Payload Example

```json
{
  "event": "student.enrolled",
  "timestamp": "2025-01-15T10:30:00Z",
  "data": {
    "course_id": "60a7c8b5c9f4a12345678901",
    "course_title": "Advanced Database Systems",
    "student_id": "STU001",
    "student_name": "John Doe",
    "enrollment_id": "60a7c8b5c9f4a12345678904"
  }
}
```

## SDK and Client Libraries

### JavaScript/Node.js

```javascript
import CourseAPI from '@comp5241/course-api';

const api = new CourseAPI({
  baseURL: 'http://localhost:5000/api/courses',
  token: 'your-jwt-token'
});

// Get courses
const courses = await api.courses.list({
  page: 1,
  category: 'Computer Science'
});

// Create course
const newCourse = await api.courses.create({
  title: 'Advanced Database Systems',
  course_code: 'COMP5241',
  // ...
});
```

### Python

```python
from comp5241_course_api import CourseAPI

api = CourseAPI(
    base_url='http://localhost:5000/api/courses',
    token='your-jwt-token'
)

# Get courses
courses = api.courses.list(page=1, category='Computer Science')

# Create course
new_course = api.courses.create({
    'title': 'Advanced Database Systems',
    'course_code': 'COMP5241',
    # ...
})
```

## Frontend Interfaces

The Course Management API is integrated with complete frontend interfaces:

### Teacher Interfaces
- **Teacher Dashboard**: `http://localhost:5000/teacher-dashboard` - Overview and statistics
- **Course Management**: `http://localhost:5000/courses` - Advanced course administration 
- **Materials Management**: `materials.html` - Upload and manage course materials

### Student Interfaces  
- **Student Dashboard**: `http://localhost:5000/student-dashboard` - Learning progress overview
- **Course Browser**: `student-courses.html` - Browse and enroll in courses
- **Materials Portal**: `student-materials.html` - Access and download course materials

### Sample Data Files
- **Student Import**: `frontend/sample_students.csv` - Ready-to-use student data
- **Teacher Import**: `frontend/sample_teachers.csv` - Ready-to-use teacher data

### Test Server for Frontend Development
```bash
# Start standalone test server (no database required)
python backend/tests/test_server.py

# Access interfaces at:
http://localhost:5001/teacher-dashboard.html
http://localhost:5001/courses.html
http://localhost:5001/student-dashboard.html
http://localhost:5001/materials.html
http://localhost:5001/student-courses.html
http://localhost:5001/student-materials.html
```

## Testing the API

### Production Testing Procedure

#### 1. Authentication Setup
```bash
# Get JWT token for testing
TOKEN=$(curl -s -X POST http://localhost:5000/api/security/login \
  -H "Content-Type: application/json" \
  -d '{"username":"teacher1","password":"password123"}' \
  | jq -r '.access_token')

echo "JWT Token: $TOKEN"
```

#### 2. API Health Check
```bash
# Test API availability
curl -X GET "http://localhost:5000/api/courses/health" \
  -H "Authorization: Bearer $TOKEN"

# Expected response:
# {"status": "healthy", "module": "courses", "message": "Courses module is running"}
```

### Using cURL

#### Course Management
```bash
# Get courses with pagination
curl -X GET "http://localhost:5000/api/courses/?page=1&per_page=10" \
  -H "Authorization: Bearer $TOKEN"

# Create course
curl -X POST "http://localhost:5000/api/courses/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Advanced Database Systems",
    "course_code": "COMP5241",
    "description": "Advanced topics in database systems",
    "category": "Computer Science",
    "difficulty_level": "advanced",
    "max_students": 50,
    "semester": "Fall 2025",
    "university": "PolyU",
    "is_published": true
  }'

# Get specific course
COURSE_ID="your_course_id_here"
curl -X GET "http://localhost:5000/api/courses/$COURSE_ID?include_stats=true" \
  -H "Authorization: Bearer $TOKEN"
```

#### Student Management
```bash
# Import students via CSV (use sample file for testing)
curl -X POST "http://localhost:5000/api/courses/$COURSE_ID/students/import" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@frontend/sample_students.csv"

# Get course students
curl -X GET "http://localhost:5000/api/courses/$COURSE_ID/students?page=1&per_page=20" \
  -H "Authorization: Bearer $TOKEN"

# Export students
curl -X GET "http://localhost:5000/api/courses/$COURSE_ID/students/export" \
  -H "Authorization: Bearer $TOKEN" \
  -o "students_export.csv"
```

#### Material Management
```bash
# Upload material
curl -X POST "http://localhost:5000/api/courses/$COURSE_ID/materials" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@lecture1.pdf" \
  -F "title=Database Fundamentals - Week 1" \
  -F "description=Introduction to database concepts" \
  -F "category=lecture" \
  -F "is_published=true"

# Get materials
curl -X GET "http://localhost:5000/api/courses/$COURSE_ID/materials?category=lecture" \
  -H "Authorization: Bearer $TOKEN"

# Download material
MATERIAL_ID="your_material_id_here"
curl -X GET "http://localhost:5000/api/courses/materials/$MATERIAL_ID/download" \
  -H "Authorization: Bearer $TOKEN" \
  -o "downloaded_material.pdf"
```

#### Announcements
```bash
# Create announcement
curl -X POST "http://localhost:5000/api/courses/$COURSE_ID/announcements" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important: Midterm Exam",
    "content": "The midterm exam will be held on October 15th at 2:00 PM.",
    "is_published": true,
    "is_pinned": true,
    "is_urgent": false
  }'

# Get announcements
curl -X GET "http://localhost:5000/api/courses/$COURSE_ID/announcements?page=1" \
  -H "Authorization: Bearer $TOKEN"
```

### Performance Testing
```bash
# Load test with Apache Bench
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/courses/"

# Concurrent upload test
for i in {1..5}; do
  curl -X POST "http://localhost:5000/api/courses/$COURSE_ID/materials" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@test_file_$i.pdf" \
    -F "title=Test Material $i" \
    -F "category=other" &
done
wait
```

### Using Postman

#### Setup Instructions
1. **Import Collection**
   ```bash
   # If Postman collection exists
   curl -o course_management.postman_collection.json \
     https://raw.githubusercontent.com/COMP5241-2526Sem1/groupproject-team_10/main/docs/postman/course_management.json
   ```

2. **Environment Variables**
   ```json
   {
     "base_url": "http://localhost:5000/api/courses",
     "auth_url": "http://localhost:5000/api/security",
     "jwt_token": "{{obtained_from_login}}",
     "course_id": "{{created_course_id}}",
     "material_id": "{{uploaded_material_id}}"
   }
   ```

3. **Pre-request Scripts** (for automatic token refresh)
   ```javascript
   // Login and set token
   pm.sendRequest({
     url: pm.environment.get("auth_url") + "/login",
     method: 'POST',
     header: {'Content-Type': 'application/json'},
     body: {
       mode: 'raw',
       raw: JSON.stringify({
         username: "teacher1",
         password: "password123"
       })
     }
   }, function (err, response) {
     if (!err && response.code === 200) {
       const token = response.json().access_token;
       pm.environment.set("jwt_token", token);
     }
   });
   ```

### Automated Testing Scripts

#### Python Testing Script
```python
import requests
import json

class CourseAPITester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.token = None
    
    def login(self, username="teacher1", password="password123"):
        response = requests.post(
            f"{self.base_url}/api/security/login",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            return True
        return False
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_course_creation(self):
        data = {
            "title": "Test Course",
            "course_code": "TEST101",
            "description": "Test course for API testing",
            "category": "Computer Science",
            "max_students": 30
        }
        response = requests.post(
            f"{self.base_url}/api/courses/",
            json=data,
            headers=self.get_headers()
        )
        return response.status_code == 201

# Usage
tester = CourseAPITester()
if tester.login():
    print("✅ Authentication successful")
    if tester.test_course_creation():
        print("✅ Course creation test passed")
    else:
        print("❌ Course creation test failed")
else:
    print("❌ Authentication failed")
```

### Test Results Validation

#### Expected Response Codes
- `200`: Successful GET, PUT, DELETE operations
- `201`: Successful POST operations (creation)
- `400`: Bad request (validation errors)
- `401`: Unauthorized (invalid/missing token)
- `403`: Forbidden (insufficient permissions)
- `404`: Resource not found
- `409`: Conflict (duplicate resource)
- `413`: Payload too large (file size limit)

#### Response Time Benchmarks
- Course listing: < 200ms
- Course creation: < 500ms
- File upload (10MB): < 2000ms
- CSV import (100 students): < 3000ms
- Material download: < 100ms + transfer time

---

For more information, refer to the main [Course Management Guide](course_management_guide.md) or contact the development team.