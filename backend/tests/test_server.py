#!/usr/bin/env python3
"""
Test server for previewing frontend pages without database operations

This server provides:
- Static file serving for HTML pages
- Mock API endpoints for testing frontend functionality
- CORS support for local development
- No database dependencies

Usage:
    python backend/tests/test_server.py
    
Then browse:
    http://localhost:5001/teacher-dashboard.html
    http://localhost:5001/courses.html
    http://localhost:5001/student-dashboard.html
"""

import os
import sys
from datetime import datetime
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

app = Flask(__name__, 
            static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend', 'static'),
            static_url_path='/static')
CORS(app)

# Get the frontend directory path
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'frontend')

@app.route('/test')
def test_index():
    """Landing page with links to all test pages"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Course Management Test Environment</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <div class="row justify-content-center">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h1 class="card-title mb-0">
                            <i class="fas fa-graduation-cap"></i>
                            Course Management Test Environment
                        </h1>
                    </div>
                    <div class="card-body">
                        <p class="lead">Welcome to the COMP5241 Group 10 Course Management Module test environment.</p>
                        
                        <h3>📋 Course Management & Teacher Tools Test Environment:</h3>
                        
                        <div class="row">
                            <div class="col-md-12">
                                <div class="list-group mb-4">
                                    <a href="/teacher-dashboard.html" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h5 class="mb-1"><i class="bi bi-speedometer2"></i> Teacher Dashboard</h5>
                                            <small class="badge bg-primary">Core</small>
                                        </div>
                                        <p class="mb-1">Comprehensive analytics, statistics, and teacher overview with course metrics.</p>
                                    </a>
                                    <a href="/courses.html" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h5 class="mb-1"><i class="bi bi-book"></i> Course Management</h5>
                                            <small class="badge bg-success">Core + CSV</small>
                                        </div>
                                        <p class="mb-1">Full course management with <strong>CSV import/export</strong>, student enrollment, materials, and announcements.</p>
                                    </a>
                                    <a href="/student-dashboard.html" class="list-group-item list-group-item-action">
                                        <div class="d-flex w-100 justify-content-between">
                                            <h5 class="mb-1"><i class="bi bi-mortarboard"></i> Student Dashboard</h5>
                                            <small class="badge bg-info">Core</small>
                                        </div>
                                        <p class="mb-1">Student view for course access, progress tracking, and materials download.</p>
                                    </a>
                                </div>
                                
                                <div class="alert alert-success">
                                    <h6><i class="bi bi-check-circle"></i> Key Features Available:</h6>
                                    <ul class="mb-0">
                                        <li><strong>CSV Import/Export:</strong> Bulk student management with error reporting</li>
                                        <li><strong>Course Analytics:</strong> Enrollment stats, material usage, and activity tracking</li>
                                        <li><strong>Material Management:</strong> File upload, download tracking, and organization</li>
                                        <li><strong>Announcements:</strong> Course communication with scheduling and priority</li>
                                        <li><strong>Student Tracking:</strong> Progress monitoring and enrollment management</li>
                                    </ul>
                                </div>
                            </div>
                        </div>                        <hr>
                        
                        <h3>API Endpoints (Mock Data):</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <ul class="list-unstyled">
                                    <li><code>GET /api/dashboard/teacher-stats</code></li>
                                    <li><code>GET /api/courses/</code></li>
                                    <li><code>GET /api/courses/{id}/students</code></li>
                                    <li><code>GET /api/courses/{id}/materials</code></li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <ul class="list-unstyled">
                                    <li><code>GET /api/dashboard/student-stats</code></li>
                                    <li><code>GET /api/courses/{id}/announcements</code></li>
                                    <li><code>GET /api/courses/import-history</code></li>
                                    <li><code>GET /api/courses/recent-activity</code></li>
                                </ul>
                            </div>
                        </div>
                        
                        <div class="alert alert-info">
                            <strong>Note:</strong> This is a test environment with mock data. No actual database operations are performed.
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    '''

@app.route('/<path:filename>')
def serve_frontend(filename):
    """Serve static files from frontend directory"""
    try:
        return send_from_directory(FRONTEND_DIR, filename)
    except FileNotFoundError:
        # Additional debug information
        print(f"File not found: {filename}")
        print(f"Looking in directory: {FRONTEND_DIR}")
        return f"File not found: {filename}<br>Looking in: {FRONTEND_DIR}", 404

# Debug route to check static files
@app.route('/debug/static')
def debug_static():
    """Debug endpoint to check static file configuration"""
    import os
    static_dir = app.static_folder
    files = []
    if os.path.exists(static_dir):
        for root, dirs, filenames in os.walk(static_dir):
            for file in filenames:
                rel_path = os.path.relpath(os.path.join(root, file), static_dir)
                files.append(rel_path)
    
    return f"""
    <h2>Static File Debug</h2>
    <p><strong>Static folder:</strong> {static_dir}</p>
    <p><strong>Static URL path:</strong> {app.static_url_path}</p>
    <p><strong>Frontend directory:</strong> {FRONTEND_DIR}</p>
    <h3>Available static files:</h3>
    <ul>{''.join([f'<li><a href="/static/{f}">{f}</a></li>' for f in files])}</ul>
    """

# Mock API endpoints for testing frontend without database

@app.route('/api/health')
def mock_health():
    """Mock health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Test server API is running',
        'environment': 'test'
    })

@app.route('/api/dashboard/teacher-stats')
def mock_teacher_stats():
    """Mock teacher dashboard statistics"""
    return jsonify({
        "success": True,
        "data": {
            "total_courses": 5,
            "total_students": 150,
            "total_materials": 23,
            "total_downloads": 456,
            "active_courses": 4,
            "draft_courses": 1,
            "recent_enrollments": [
                {
                    "student_name": "John Doe",
                    "course_title": "Advanced Database Systems",
                    "enrolled_at": "2025-01-15T10:30:00Z"
                },
                {
                    "student_name": "Jane Smith", 
                    "course_title": "Machine Learning Fundamentals",
                    "enrolled_at": "2025-01-15T14:20:00Z"
                },
                {
                    "student_name": "Mike Johnson",
                    "course_title": "Web Development",
                    "enrolled_at": "2025-01-16T09:15:00Z"
                }
            ],
            "recent_downloads": [
                {
                    "student_name": "Sarah Wilson",
                    "material_title": "Week 1 Lecture Notes",
                    "course_title": "Database Systems",
                    "downloaded_at": "2025-01-16T16:45:00Z"
                },
                {
                    "student_name": "David Chen",
                    "material_title": "Assignment 1 Guidelines", 
                    "course_title": "Machine Learning",
                    "downloaded_at": "2025-01-16T15:30:00Z"
                }
            ],
            "import_history": [
                {
                    "course_title": "Advanced Database Systems",
                    "imported_at": "2025-01-10T09:00:00Z",
                    "successful_count": 45,
                    "failed_count": 2,
                    "status": "completed"
                },
                {
                    "course_title": "Machine Learning Fundamentals",
                    "imported_at": "2025-01-12T14:30:00Z", 
                    "successful_count": 38,
                    "failed_count": 0,
                    "status": "completed"
                }
            ]
        }
    })

@app.route('/api/courses/')
def mock_courses():
    """Mock courses list with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    courses = [
        {
            "id": "1",
            "title": "Advanced Database Systems",
            "course_code": "COMP5241",
            "description": "Advanced topics in database systems including NoSQL, distributed databases, and big data processing.",
            "category": "Computer Science",
            "difficulty_level": "advanced",
            "teacher_name": "Dr. Smith",
            "student_count": 45,
            "max_students": 50,
            "is_published": True,
            "semester": "Fall 2025",
            "university": "PolyU",
            "created_at": "2025-01-01T10:00:00Z",
            "materials_count": 12,
            "announcements_count": 3
        },
        {
            "id": "2",
            "title": "Machine Learning Fundamentals", 
            "course_code": "COMP5318",
            "description": "Introduction to machine learning concepts, algorithms, and applications.",
            "category": "Computer Science",
            "difficulty_level": "intermediate",
            "teacher_name": "Prof. Johnson",
            "student_count": 38,
            "max_students": 40,
            "is_published": True,
            "semester": "Fall 2025",
            "university": "PolyU",
            "created_at": "2025-01-02T11:00:00Z",
            "materials_count": 8,
            "announcements_count": 2
        },
        {
            "id": "3",
            "title": "Web Development Bootcamp",
            "course_code": "COMP3322",
            "description": "Comprehensive web development course covering HTML, CSS, JavaScript, and modern frameworks.",
            "category": "Computer Science", 
            "difficulty_level": "beginner",
            "teacher_name": "Dr. Wilson",
            "student_count": 67,
            "max_students": 80,
            "is_published": True,
            "semester": "Fall 2025",
            "university": "PolyU",
            "created_at": "2025-01-03T09:30:00Z",
            "materials_count": 15,
            "announcements_count": 5
        },
        {
            "id": "4",
            "title": "Data Structures and Algorithms",
            "course_code": "COMP2011",
            "description": "Fundamental data structures and algorithms for computer science.",
            "category": "Computer Science",
            "difficulty_level": "intermediate", 
            "teacher_name": "Prof. Brown",
            "student_count": 0,
            "max_students": 60,
            "is_published": False,
            "semester": "Spring 2026",
            "university": "PolyU",
            "created_at": "2025-01-04T14:15:00Z",
            "materials_count": 0,
            "announcements_count": 0
        }
    ]
    
    # Filter courses based on search and category
    filtered_courses = courses
    if search:
        filtered_courses = [c for c in filtered_courses if search.lower() in c['title'].lower() or search.lower() in c['course_code'].lower()]
    if category:
        filtered_courses = [c for c in filtered_courses if c['category'] == category]
        
    return jsonify({
        "success": True,
        "data": {
            "courses": filtered_courses,
            "total": len(filtered_courses)
        },
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(filtered_courses),
            "pages": 1,
            "has_next": False,
            "has_prev": False
        }
    })

@app.route('/api/courses/<course_id>/students')
def mock_course_students(course_id):
    """Mock course students list"""
    students = [
        {
            "id": "1",
            "student_id": "STU001",
            "student_name": "John Doe",
            "email": "john.doe@student.edu",
            "university": "PolyU",
            "enrolled_at": "2025-01-05T09:30:00Z",
            "progress": 75.5,
            "last_activity": "2025-01-15T16:45:00Z",
            "status": "active"
        },
        {
            "id": "2",
            "student_id": "STU002", 
            "student_name": "Jane Smith",
            "email": "jane.smith@student.edu",
            "university": "HKU",
            "enrolled_at": "2025-01-06T10:15:00Z",
            "progress": 82.3,
            "last_activity": "2025-01-16T14:20:00Z",
            "status": "active"
        },
        {
            "id": "3",
            "student_id": "STU003",
            "student_name": "Mike Johnson", 
            "email": "mike.johnson@student.edu",
            "university": "PolyU",
            "enrolled_at": "2025-01-07T11:45:00Z",
            "progress": 68.9,
            "last_activity": "2025-01-15T12:30:00Z",
            "status": "active"
        }
    ]
    
    return jsonify({
        "success": True,
        "data": students,
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": len(students),
            "pages": 1
        }
    })

@app.route('/api/courses/<course_id>/materials')
def mock_course_materials(course_id):
    """Mock course materials list"""
    materials = [
        {
            "id": "1",
            "title": "Database Fundamentals - Week 1",
            "description": "Introduction to database concepts",
            "category": "lecture",
            "file_name": "week1_fundamentals.pdf",
            "file_size": 2048576,
            "file_type": "application/pdf",
            "is_published": True,
            "published_at": "2025-01-01T08:00:00Z",
            "download_count": 45,
            "uploaded_at": "2025-01-01T07:45:00Z"
        },
        {
            "id": "2",
            "title": "Assignment 1 - ER Diagrams",
            "description": "Create entity-relationship diagrams for given scenarios",
            "category": "assignment", 
            "file_name": "assignment1_er.pdf",
            "file_size": 1536000,
            "file_type": "application/pdf",
            "is_published": True,
            "published_at": "2025-01-08T09:00:00Z",
            "download_count": 38,
            "uploaded_at": "2025-01-08T08:30:00Z"
        },
        {
            "id": "3",
            "title": "SQL Tutorial Videos",
            "description": "Comprehensive SQL tutorial video series",
            "category": "media",
            "file_name": "sql_tutorials.zip", 
            "file_size": 50331648,
            "file_type": "application/zip",
            "is_published": True,
            "published_at": "2025-01-10T10:00:00Z",
            "download_count": 29,
            "uploaded_at": "2025-01-10T09:15:00Z"
        }
    ]
    
    return jsonify({
        "success": True,
        "data": materials,
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": len(materials),
            "pages": 1
        }
    })

@app.route('/api/courses/<course_id>/announcements')
def mock_course_announcements(course_id):
    """Mock course announcements list"""
    announcements = [
        {
            "id": "1",
            "title": "Important: Midterm Exam Schedule",
            "content": "The midterm exam will be held on February 15th at 2:00 PM in Room A101. Please bring your student ID and calculator.",
            "is_published": True,
            "is_pinned": True,
            "is_urgent": False,
            "published_at": "2025-01-10T09:00:00Z",
            "expires_at": "2025-02-15T23:59:59Z",
            "created_at": "2025-01-10T08:45:00Z",
            "author_name": "Dr. Smith"
        },
        {
            "id": "2",
            "title": "Week 3 Materials Available",
            "content": "New lecture materials for Week 3 have been uploaded. Topics include normalization and database design principles.",
            "is_published": True,
            "is_pinned": False,
            "is_urgent": False,
            "published_at": "2025-01-12T10:00:00Z",
            "expires_at": None,
            "created_at": "2025-01-12T09:45:00Z",
            "author_name": "Dr. Smith"
        }
    ]
    
    return jsonify({
        "success": True,
        "data": announcements,
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": len(announcements),
            "pages": 1
        }
    })

@app.route('/api/dashboard/student-stats')
def mock_student_stats():
    """Mock student dashboard statistics"""
    return jsonify({
        "success": True,
        "data": {
            "enrolled_courses": [
                {
                    "id": "1",
                    "title": "Advanced Database Systems",
                    "course_code": "COMP5241",
                    "teacher_name": "Dr. Smith",
                    "progress": 75.5,
                    "last_activity": "2025-01-15T16:45:00Z",
                    "next_deadline": "2025-01-20T23:59:59Z",
                    "materials_count": 12,
                    "announcements_count": 3
                },
                {
                    "id": "2",
                    "title": "Machine Learning Fundamentals",
                    "course_code": "COMP5318", 
                    "teacher_name": "Prof. Johnson",
                    "progress": 82.3,
                    "last_activity": "2025-01-16T14:20:00Z",
                    "next_deadline": "2025-01-25T23:59:59Z",
                    "materials_count": 8,
                    "announcements_count": 2
                },
                {
                    "id": "3",
                    "title": "Web Development Bootcamp",
                    "course_code": "COMP3322",
                    "teacher_name": "Dr. Wilson", 
                    "progress": 68.9,
                    "last_activity": "2025-01-15T12:30:00Z",
                    "next_deadline": "2025-01-18T23:59:59Z",
                    "materials_count": 15,
                    "announcements_count": 5
                }
            ],
            "recent_announcements": [
                {
                    "id": "1",
                    "course_title": "Advanced Database Systems",
                    "title": "Midterm Exam Schedule",
                    "content": "The midterm exam will be held on February 15th...",
                    "published_at": "2025-01-10T09:00:00Z",
                    "is_urgent": False,
                    "is_pinned": True
                },
                {
                    "id": "2",
                    "course_title": "Machine Learning Fundamentals",
                    "title": "New Assignment Posted",
                    "content": "Assignment 2 on neural networks is now available...",
                    "published_at": "2025-01-12T14:30:00Z",
                    "is_urgent": False,
                    "is_pinned": False
                }
            ],
            "recent_materials": [
                {
                    "id": "1",
                    "course_title": "Advanced Database Systems",
                    "title": "Week 3 Lecture Notes",
                    "category": "lecture",
                    "uploaded_at": "2025-01-12T10:00:00Z",
                    "file_size": 2048576
                },
                {
                    "id": "2",
                    "course_title": "Web Development Bootcamp",
                    "title": "JavaScript Tutorial Videos",
                    "category": "media",
                    "uploaded_at": "2025-01-14T16:00:00Z",
                    "file_size": 25165824
                }
            ],
            "statistics": {
                "total_courses": 3,
                "completed_courses": 0,
                "total_downloads": 24,
                "average_progress": 75.6
            }
        }
    })

@app.route('/api/courses/import-history')
def mock_import_history_dashboard():
    """Mock import history for teacher dashboard"""
    return jsonify({
        "success": True,
        "data": [
            {
                "id": "1",
                "course_title": "Advanced Database Systems",
                "course_id": "1",
                "imported_at": "2025-01-10T09:00:00Z",
                "total_records": 50,
                "successful_count": 45,
                "failed_count": 3,
                "duplicate_count": 2,
                "status": "completed",
                "file_name": "students_comp5241.csv"
            },
            {
                "id": "2", 
                "course_title": "Machine Learning Fundamentals",
                "course_id": "2",
                "imported_at": "2025-01-12T14:30:00Z",
                "total_records": 40,
                "successful_count": 38,
                "failed_count": 0,
                "duplicate_count": 2,
                "status": "completed",
                "file_name": "ml_students.csv"
            }
        ]
    })

@app.route('/api/courses/recent-activity')
def mock_recent_activity():
    """Mock recent activity for dashboards"""
    return jsonify({
        "success": True,
        "data": {
            "enrollments": [
                {
                    "student_name": "Alice Brown",
                    "course_title": "Advanced Database Systems", 
                    "enrolled_at": "2025-01-16T10:30:00Z",
                    "type": "enrollment"
                },
                {
                    "student_name": "Bob Wilson",
                    "course_title": "Machine Learning Fundamentals",
                    "enrolled_at": "2025-01-16T11:15:00Z",
                    "type": "enrollment"
                }
            ],
            "downloads": [
                {
                    "student_name": "Carol Davis",
                    "material_title": "Week 1 Lecture Notes",
                    "course_title": "Database Systems",
                    "downloaded_at": "2025-01-16T16:45:00Z",
                    "type": "download"
                },
                {
                    "student_name": "David Chen",
                    "material_title": "Assignment Guidelines",
                    "course_title": "Machine Learning",
                    "downloaded_at": "2025-01-16T15:30:00Z",
                    "type": "download"
                }
            ]
        }
    })

# Additional mock endpoints for complete dashboard functionality
@app.route('/api/courses/teacher/dashboard')
def mock_teacher_dashboard():
    """Mock comprehensive teacher dashboard stats"""
    return jsonify({
        "success": True,
        "stats": {
            "courses": {
                "total": 5,
                "published": 4,
                "active": 4
            },
            "students": {
                "total_enrollments": 156,
                "active_students": 142,
                "completed": 8
            },
            "materials": {
                "total": 47,
                "total_downloads": 1234,
                "published": 42
            },
            "announcements": {
                "total": 23,
                "pinned": 3
            },
            "recent_activity": {
                "enrollments": [
                    {"student_name": "Alice Johnson", "course_title": "COMP5241", "enrolled_at": "2025-01-20T10:30:00Z"},
                    {"student_name": "Bob Smith", "course_title": "COMP5242", "enrolled_at": "2025-01-20T09:15:00Z"}
                ],
                "downloads": [
                    {"material_title": "Week 3 Notes", "downloaded_by": "Charlie Brown", "downloaded_at": "2025-01-20T11:45:00Z"},
                    {"material_title": "Assignment 2", "downloaded_by": "Diana Prince", "downloaded_at": "2025-01-20T11:30:00Z"}
                ]
            }
        }
    })

@app.route('/api/courses/')
@app.route('/api/courses')
def mock_courses_list():
    """Mock courses list endpoint"""
    return jsonify({
        "success": True,
        "courses": [
            {
                "id": "course1",
                "title": "Advanced Web Development",
                "course_code": "COMP5241",
                "description": "Learn modern web development with React, Node.js, and MongoDB",
                "instructor_name": "Dr. Sarah Johnson",
                "current_enrollment": 42,
                "max_students": 50,
                "is_published": True,
                "semester": "Fall 2025"
            },
            {
                "id": "course2", 
                "title": "Database Systems",
                "course_code": "COMP5242",
                "description": "Comprehensive introduction to database design and management",
                "instructor_name": "Prof. Michael Chen",
                "current_enrollment": 38,
                "max_students": 45,
                "is_published": True,
                "semester": "Fall 2025"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 2,
            "pages": 1
        }
    })

# CSV Import/Export Mock Endpoints
@app.route('/api/courses/<course_id>/students/import', methods=['POST'])
def mock_import_students(course_id):
    """Mock student CSV import endpoint"""
    return jsonify({
        "success": True,
        "results": {
            "total_records": 25,
            "successful_imports": 22,
            "failed_imports": 2,
            "duplicate_records": 1,
            "import_log_id": "mock_import_123",
            "batch_id": "batch_456",
            "errors": [
                {
                    "row": 15,
                    "error": "Missing student_id",
                    "data": {"student_name": "John Doe", "email": "john@example.com"}
                },
                {
                    "row": 23,
                    "error": "Student S12345 already enrolled",
                    "data": {"student_id": "S12345", "student_name": "Jane Smith"}
                }
            ]
        },
        "message": "Import completed with 22/25 successful imports"
    })

@app.route('/api/courses/<course_id>/students/export', methods=['GET'])
def mock_export_students(course_id):
    """Mock student CSV export endpoint"""
    from flask import make_response
    
    # Mock CSV data
    csv_data = """student_id,student_name,student_email,enrollment_date,status,progress_percentage,university
S001,Alice Johnson,alice.johnson@student.edu,2025-01-15 10:30:00,enrolled,85.5,PolyU
S002,Bob Smith,bob.smith@student.edu,2025-01-15 11:15:00,enrolled,72.0,PolyU
S003,Carol Davis,carol.davis@student.edu,2025-01-16 09:45:00,enrolled,91.2,PolyU
S004,David Chen,david.chen@student.edu,2025-01-16 14:20:00,enrolled,68.8,PolyU
S005,Emma Wilson,emma.wilson@student.edu,2025-01-17 16:30:00,enrolled,77.3,PolyU"""
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=students_{course_id}.csv'
    return response

@app.route('/api/courses/imports/<import_log_id>/errors/export', methods=['GET'])
def mock_export_import_errors(import_log_id):
    """Mock import errors CSV export endpoint"""
    from flask import make_response
    
    # Mock error CSV data
    csv_data = """student_id,student_name,student_email,error_type,error_message,row_number
,John Doe,john@example.com,missing_field,Missing student_id,15
S12345,Jane Smith,jane@example.com,duplicate,Student S12345 already enrolled,23"""
    
    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=import_errors_{import_log_id}.csv'
    return response

@app.route('/api/courses/teacher/imports', methods=['GET'])
def mock_import_history():
    """Mock import history endpoint"""
    return jsonify({
        "success": True,
        "import_logs": [
            {
                "id": "import_123",
                "batch_id": "batch_456",
                "course_id": "course1",
                "course_title": "Advanced Web Development",
                "original_filename": "students_batch1.csv",
                "total_records": 25,
                "successful_imports": 22,
                "failed_imports": 2,
                "duplicate_records": 1,
                "status": "completed",
                "started_at": "2025-01-20T10:00:00Z",
                "completed_at": "2025-01-20T10:02:15Z"
            },
            {
                "id": "import_124",
                "batch_id": "batch_457",
                "course_id": "course2",
                "course_title": "Database Systems",
                "original_filename": "db_students.csv",
                "total_records": 18,
                "successful_imports": 18,
                "failed_imports": 0,
                "duplicate_records": 0,
                "status": "completed",
                "started_at": "2025-01-19T14:30:00Z",
                "completed_at": "2025-01-19T14:31:02Z"
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 2,
            "pages": 1
        }
    })

if __name__ == '__main__':
    print(f"Frontend directory: {FRONTEND_DIR}")
    print(f"Frontend directory exists: {os.path.exists(FRONTEND_DIR)}")
    print("=" * 60)
    print("🚀 COMP5241 Group 10 - Course Management Test Server")
    print("=" * 60)
    print("📋 Available endpoints:")
    print("   🏠 Main page: http://localhost:5001")
    print("   👨‍🏫 Teacher Dashboard: http://localhost:5001/teacher-dashboard.html")
    print("   📚 Course Management: http://localhost:5001/courses.html")
    print("   👨‍🎓 Student Dashboard: http://localhost:5001/student-dashboard.html")
    print("=" * 60)
    print("🧪 Mock API endpoints available for frontend testing")
    print("✨ No database required - all mock data provided")
    print("=" * 60)
    
    app.run(debug=True, port=5001, host='0.0.0.0')