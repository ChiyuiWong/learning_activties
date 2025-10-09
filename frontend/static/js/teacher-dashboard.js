/*
COMP5241 Group 10 - Teacher Dashboard JavaScript
Enhanced course management and teacher tools functionality
*/

// Global variables
let currentUser = null;
let dashboardStats = null;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthAndRole('teacher');
    
    // Initialize dashboard
    initializeDashboard();
    
    // Set up event listeners
    setupEventListeners();
});

function checkAuthAndRole(requiredRole) {
    // This would typically check JWT token and role
    // For now, we'll simulate it
    currentUser = {
        id: 'teacher123',
        username: 'Dr. Smith',
        role: 'teacher',
        email: 'smith@university.edu'
    };
    
    if (currentUser.role !== requiredRole) {
        window.location.href = '/login.html';
        return;
    }
}

function setupEventListeners() {
    // Create course form
    document.getElementById('createCourseForm').addEventListener('submit', handleCreateCourse);
    
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });
}

async function initializeDashboard() {
    try {
        showLoading(true);
        
        // Load dashboard statistics
        await loadDashboardStats();
        
        // Load recent courses
        await loadRecentCourses();
        
        // Load recent activity
        await loadRecentActivity();
        
        // Load import history
        await loadImportHistory();
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showAlert('Failed to load dashboard data', 'danger');
    } finally {
        showLoading(false);
    }
}

async function loadDashboardStats() {
    try {
        // Simulate API call to get teacher dashboard stats
        // const response = await CoursesAPI.getTeacherDashboard();
        
        // Mock data for preview
        dashboardStats = {
            courses: {
                total: 5,
                published: 4,
                active: 5
            },
            students: {
                total_enrollments: 127,
                active_students: 115,
                completed: 12
            },
            materials: {
                total: 23,
                total_downloads: 456,
                published: 20
            },
            announcements: {
                total: 8,
                pinned: 2
            }
        };
        
        // Update UI
        updateStatsCards();
        
    } catch (error) {
        console.error('Error loading dashboard stats:', error);
        // Show default values
        updateStatsCards();
    }
}

function updateStatsCards() {
    if (dashboardStats) {
        document.getElementById('totalCourses').textContent = dashboardStats.courses.total;
        document.getElementById('totalStudents').textContent = dashboardStats.students.total_enrollments;
        document.getElementById('totalMaterials').textContent = dashboardStats.materials.total;
        document.getElementById('totalDownloads').textContent = dashboardStats.materials.total_downloads;
    } else {
        // Default values
        document.getElementById('totalCourses').textContent = '0';
        document.getElementById('totalStudents').textContent = '0';
        document.getElementById('totalMaterials').textContent = '0';
        document.getElementById('totalDownloads').textContent = '0';
    }
}

async function loadRecentCourses() {
    try {
        const container = document.getElementById('coursesContainer');
        
        // Simulate API call
        // const response = await CoursesAPI.getCourses({ page: 1, per_page: 5 });
        
        // Mock data
        const courses = [
            {
                id: '1',
                title: 'Advanced Database Systems',
                course_code: 'COMP5241',
                current_enrollment: 45,
                max_students: 50,
                is_published: true,
                semester: 'Fall 2025'
            },
            {
                id: '2',
                title: 'Machine Learning Fundamentals',
                course_code: 'COMP4321',
                current_enrollment: 38,
                max_students: 40,
                is_published: true,
                semester: 'Fall 2025'
            },
            {
                id: '3',
                title: 'Web Development',
                course_code: 'COMP3421',
                current_enrollment: 25,
                max_students: 30,
                is_published: false,
                semester: 'Spring 2026'
            }
        ];
        
        // Render courses
        container.innerHTML = '';
        if (courses.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-book fs-1"></i>
                    <p>No courses yet. <a href="#" data-bs-toggle="modal" data-bs-target="#createCourseModal">Create your first course</a></p>
                </div>
            `;
        } else {
            courses.forEach(course => {
                const courseCard = createCourseCard(course);
                container.appendChild(courseCard);
            });
        }
        
    } catch (error) {
        console.error('Error loading courses:', error);
        document.getElementById('coursesContainer').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> Failed to load courses
            </div>
        `;
    }
}

function createCourseCard(course) {
    const card = document.createElement('div');
    card.className = 'card mb-3';
    
    const progressPercentage = Math.round((course.current_enrollment / course.max_students) * 100);
    const statusBadge = course.is_published ? 
        '<span class="badge bg-success">Published</span>' : 
        '<span class="badge bg-warning">Draft</span>';
    
    card.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="card-title">${course.title}</h6>
                    <p class="card-text text-muted">${course.course_code} • ${course.semester}</p>
                    <small class="text-muted">
                        <i class="bi bi-people"></i> ${course.current_enrollment}/${course.max_students} students
                    </small>
                </div>
                <div class="text-end">
                    ${statusBadge}
                    <div class="mt-2">
                        <button class="btn btn-sm btn-outline-primary" onclick="viewCourse('${course.id}')">
                            <i class="bi bi-eye"></i> View
                        </button>
                    </div>
                </div>
            </div>
            <div class="progress mt-2" style="height: 5px;">
                <div class="progress-bar" role="progressbar" style="width: ${progressPercentage}%"></div>
            </div>
        </div>
    `;
    
    return card;
}

async function loadRecentActivity() {
    try {
        const container = document.getElementById('recentActivity');
        
        // Mock recent activity data
        const activities = [
            {
                type: 'enrollment',
                message: 'John Doe enrolled in Advanced Database Systems',
                time: '2 hours ago',
                icon: 'bi-person-plus'
            },
            {
                type: 'download',
                message: 'Sarah Smith downloaded Lecture 5 slides',
                time: '4 hours ago',
                icon: 'bi-download'
            },
            {
                type: 'enrollment',
                message: 'Mike Johnson enrolled in Machine Learning Fundamentals',
                time: '6 hours ago',
                icon: 'bi-person-plus'
            }
        ];
        
        container.innerHTML = '';
        if (activities.length === 0) {
            container.innerHTML = '<p class="text-muted">No recent activity</p>';
        } else {
            activities.forEach(activity => {
                const activityItem = document.createElement('div');
                activityItem.className = 'mb-2';
                activityItem.innerHTML = `
                    <div class="d-flex">
                        <div class="me-2">
                            <i class="bi ${activity.icon} text-primary"></i>
                        </div>
                        <div class="flex-grow-1">
                            <small class="text-muted">${activity.message}</small>
                            <br>
                            <small class="text-muted">${activity.time}</small>
                        </div>
                    </div>
                `;
                container.appendChild(activityItem);
            });
        }
        
    } catch (error) {
        console.error('Error loading recent activity:', error);
        document.getElementById('recentActivity').innerHTML = `
            <div class="alert alert-danger alert-sm">Failed to load activity</div>
        `;
    }
}

async function loadImportHistory() {
    try {
        const container = document.getElementById('importHistoryContainer');
        
        // Mock import history data
        const imports = [
            {
                id: '1',
                course_title: 'Advanced Database Systems',
                started_at: '2025-10-07 10:30:00',
                status: 'completed',
                total_records: 45,
                successful_imports: 43,
                failed_imports: 2
            },
            {
                id: '2',
                course_title: 'Machine Learning Fundamentals',
                started_at: '2025-10-06 14:15:00',
                status: 'completed',
                total_records: 38,
                successful_imports: 38,
                failed_imports: 0
            }
        ];
        
        container.innerHTML = '';
        if (imports.length === 0) {
            container.innerHTML = '<p class="text-muted">No import history</p>';
        } else {
            const table = document.createElement('table');
            table.className = 'table table-sm';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Course</th>
                        <th>Date</th>
                        <th>Status</th>
                        <th>Results</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${imports.map(imp => `
                        <tr>
                            <td>${imp.course_title}</td>
                            <td><small>${new Date(imp.started_at).toLocaleDateString()}</small></td>
                            <td>
                                <span class="badge ${getStatusBadgeClass(imp.status)}">${imp.status}</span>
                            </td>
                            <td>
                                <small>
                                    ${imp.successful_imports}/${imp.total_records} success
                                    ${imp.failed_imports > 0 ? `<br>${imp.failed_imports} failed` : ''}
                                </small>
                            </td>
                            <td>
                                ${imp.failed_imports > 0 ? 
                                    `<button class="btn btn-sm btn-outline-danger" onclick="exportImportErrors('${imp.id}')">
                                        <i class="bi bi-download"></i> Errors
                                    </button>` : 
                                    '<small class="text-muted">-</small>'
                                }
                            </td>
                        </tr>
                    `).join('')}
                </tbody>
            `;
            container.appendChild(table);
        }
        
    } catch (error) {
        console.error('Error loading import history:', error);
        document.getElementById('importHistoryContainer').innerHTML = `
            <div class="alert alert-danger alert-sm">Failed to load import history</div>
        `;
    }
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'completed': return 'bg-success';
        case 'failed': return 'bg-danger';
        case 'processing': return 'bg-warning';
        default: return 'bg-secondary';
    }
}

async function handleCreateCourse(event) {
    event.preventDefault();
    
    try {
        const formData = new FormData(event.target);
        const courseData = {
            title: document.getElementById('courseTitle').value,
            course_code: document.getElementById('courseCode').value,
            description: document.getElementById('courseDescription').value,
            category: document.getElementById('courseCategory').value,
            difficulty_level: document.getElementById('courseDifficulty').value,
            max_students: parseInt(document.getElementById('maxStudents').value),
            semester: document.getElementById('courseSemester').value,
            university: document.getElementById('courseUniversity').value,
            is_published: document.getElementById('coursePublished').checked
        };
        
        // Validate required fields
        if (!courseData.title || !courseData.course_code) {
            showAlert('Title and course code are required', 'danger');
            return;
        }
        
        showLoading(true);
        
        // Simulate API call
        // const response = await CoursesAPI.createCourse(courseData);
        
        // Mock success response
        const response = { success: true, course_id: 'new_course_123' };
        
        if (response.success) {
            showAlert('Course created successfully!', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createCourseModal'));
            modal.hide();
            
            // Reset form
            event.target.reset();
            
            // Refresh courses list
            await loadRecentCourses();
            await loadDashboardStats();
            
        } else {
            showAlert('Failed to create course: ' + response.error, 'danger');
        }
        
    } catch (error) {
        console.error('Error creating course:', error);
        showAlert('An error occurred while creating the course', 'danger');
    } finally {
        showLoading(false);
    }
}

async function viewCourse(courseId) {
    try {
        // Find the course data from the loaded courses
        const coursesContainer = document.getElementById('coursesContainer');
        const courses = [
            {
                id: '1',
                title: 'Advanced Database Systems',
                course_code: 'COMP5241',
                description: 'Advanced topics in database systems including NoSQL, distributed databases, and big data processing.',
                current_enrollment: 45,
                max_students: 50,
                is_published: true,
                semester: 'Fall 2025',
                instructor_name: 'Dr. Smith',
                university: 'PolyU',
                created_at: '2025-09-01'
            },
            {
                id: '2',
                title: 'Machine Learning Fundamentals',
                course_code: 'COMP4321',
                description: 'Introduction to machine learning algorithms and applications.',
                current_enrollment: 38,
                max_students: 40,
                is_published: true,
                semester: 'Fall 2025',
                instructor_name: 'Dr. Smith',
                university: 'PolyU',
                created_at: '2025-09-02'
            },
            {
                id: '3',
                title: 'Web Development',
                course_code: 'COMP3421',
                description: 'Modern web development using HTML, CSS, JavaScript, and frameworks.',
                current_enrollment: 25,
                max_students: 30,
                is_published: false,
                semester: 'Spring 2026',
                instructor_name: 'Dr. Smith',
                university: 'PolyU',
                created_at: '2025-09-03'
            }
        ];
        
        const courseData = courses.find(c => c.id === courseId);
        if (!courseData) {
            showAlert('Course not found', 'danger');
            return;
        }
        
        // Show course details modal
        showTeacherCourseModal(courseData);
        
    } catch (error) {
        console.error('Error viewing course:', error);
        showAlert('Failed to load course details', 'danger');
    }
}

function showTeacherCourseModal(courseData) {
    // Set modal title
    document.getElementById('courseDetailsTitle').textContent = courseData.title;
    
    // Populate overview tab
    const progressPercentage = Math.round((courseData.current_enrollment / courseData.max_students) * 100);
    const statusBadge = courseData.is_published ? 
        '<span class="badge bg-success">Published</span>' : 
        '<span class="badge bg-warning">Draft</span>';
    
    document.getElementById('courseOverview').innerHTML = `
        <div class="row">
            <div class="col-md-8">
                <h6>Course Information</h6>
                <table class="table table-borderless">
                    <tr><td><strong>Code:</strong></td><td>${courseData.course_code}</td></tr>
                    <tr><td><strong>Instructor:</strong></td><td>${courseData.instructor_name}</td></tr>
                    <tr><td><strong>Semester:</strong></td><td>${courseData.semester}</td></tr>
                    <tr><td><strong>University:</strong></td><td>${courseData.university}</td></tr>
                    <tr><td><strong>Status:</strong></td><td>${statusBadge}</td></tr>
                </table>
                
                <h6>Description</h6>
                <p>${courseData.description}</p>
                
                <h6>Enrollment Progress</h6>
                <div class="progress mb-2" style="height: 20px;">
                    <div class="progress-bar bg-primary" 
                         role="progressbar" style="width: ${progressPercentage}%">
                        ${courseData.current_enrollment}/${courseData.max_students}
                    </div>
                </div>
                <p><small class="text-muted">Created: ${new Date(courseData.created_at).toLocaleDateString()}</small></p>
            </div>
            <div class="col-md-4">
                <h6>Quick Actions</h6>
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-primary btn-sm" onclick="loadCourseStudents('${courseData.id}')">
                        <i class="bi bi-people"></i> View Students
                    </button>
                    <button class="btn btn-outline-info btn-sm" onclick="loadCourseMaterials('${courseData.id}')">
                        <i class="bi bi-files"></i> View Materials
                    </button>
                    <button class="btn btn-outline-success btn-sm" onclick="loadCourseAnnouncements('${courseData.id}')">
                        <i class="bi bi-megaphone"></i> View Announcements
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('courseDetailsModal'));
    modal.show();
    
    // Set up tab event listeners
    document.getElementById('students-tab').addEventListener('click', () => loadCourseStudents(courseData.id));
    document.getElementById('materials-tab').addEventListener('click', () => loadCourseMaterials(courseData.id));
    document.getElementById('announcements-tab').addEventListener('click', () => loadCourseAnnouncements(courseData.id));
}

async function loadCourseStudents(courseId) {
    try {
        const container = document.getElementById('courseStudents');
        container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div></div>';
        
        // Mock students data
        const students = [
            {
                id: '1',
                student_name: 'John Doe',
                email: 'john.doe@student.edu',
                enrolled_at: '2025-09-15',
                progress: 75,
                last_activity: '2025-10-06'
            },
            {
                id: '2',
                student_name: 'Jane Smith',
                email: 'jane.smith@student.edu',
                enrolled_at: '2025-09-16',
                progress: 82,
                last_activity: '2025-10-07'
            },
            {
                id: '3',
                student_name: 'Mike Johnson',
                email: 'mike.johnson@student.edu',
                enrolled_at: '2025-09-17',
                progress: 68,
                last_activity: '2025-10-05'
            }
        ];
        
        container.innerHTML = `
            <div class="list-group">
                ${students.map(student => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="flex-grow-1">
                                <h6 class="mb-1">${student.student_name}</h6>
                                <p class="mb-1 text-muted">${student.email}</p>
                                <small class="text-muted">
                                    Enrolled: ${new Date(student.enrolled_at).toLocaleDateString()} • 
                                    Progress: ${student.progress}% • 
                                    Last active: ${new Date(student.last_activity).toLocaleDateString()}
                                </small>
                            </div>
                            <div class="text-end">
                                <div class="progress" style="width: 60px; height: 6px;">
                                    <div class="progress-bar" style="width: ${student.progress}%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading course students:', error);
        document.getElementById('courseStudents').innerHTML = `
            <div class="alert alert-danger alert-sm">Failed to load students</div>
        `;
    }
}

async function loadCourseMaterials(courseId) {
    try {
        const container = document.getElementById('courseMaterials');
        container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div></div>';
        
        // Mock materials data
        const materials = [
            {
                id: '1',
                title: 'Lecture 1 - Introduction to Database Systems',
                file_name: 'lecture1.pdf',
                file_type: 'pdf',
                uploaded_at: '2025-09-10',
                download_count: 45,
                category: 'lecture'
            },
            {
                id: '2',
                title: 'Assignment 1 - ER Modeling',
                file_name: 'assignment1.docx',
                file_type: 'docx',
                uploaded_at: '2025-09-15',
                download_count: 38,
                category: 'assignment'
            },
            {
                id: '3',
                title: 'Lab Exercise 1',
                file_name: 'lab1.zip',
                file_type: 'zip',
                uploaded_at: '2025-09-20',
                download_count: 42,
                category: 'reading'
            }
        ];
        
        container.innerHTML = `
            <div class="list-group">
                ${materials.map(material => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div class="flex-grow-1">
                                <h6 class="mb-1">${material.title}</h6>
                                <small class="text-muted">
                                    <i class="bi bi-file-earmark-${getFileIcon(material.file_type)}"></i> 
                                    ${material.file_name} • 
                                    ${getCategoryBadge(material.category)} • 
                                    ${material.download_count} downloads
                                </small>
                                <br>
                                <small class="text-muted">Uploaded: ${new Date(material.uploaded_at).toLocaleDateString()}</small>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading course materials:', error);
        document.getElementById('courseMaterials').innerHTML = `
            <div class="alert alert-danger alert-sm">Failed to load materials</div>
        `;
    }
}

async function loadCourseAnnouncements(courseId) {
    try {
        const container = document.getElementById('courseAnnouncements');
        container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div></div>';
        
        // Mock announcements data
        const announcements = [
            {
                id: '1',
                title: 'Welcome to Advanced Database Systems!',
                content: 'Welcome everyone to this exciting course. We will cover advanced topics in database systems...',
                created_at: '2025-09-01',
                is_pinned: true,
                is_urgent: false
            },
            {
                id: '2',
                title: 'Assignment 2 Due Date Extended',
                content: 'Due to popular request, the due date for Assignment 2 has been extended to next Friday.',
                created_at: '2025-10-06',
                is_pinned: false,
                is_urgent: true
            }
        ];
        
        container.innerHTML = `
            <div class="list-group">
                ${announcements.map(announcement => `
                    <div class="list-group-item ${announcement.is_urgent ? 'border-warning' : ''}">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                <h6 class="mb-1">
                                    ${announcement.title}
                                    ${announcement.is_pinned ? '<i class="bi bi-pin-angle text-warning"></i>' : ''}
                                    ${announcement.is_urgent ? '<i class="bi bi-exclamation-triangle text-warning"></i>' : ''}
                                </h6>
                                <p class="mb-1">${announcement.content}</p>
                                <small class="text-muted">${new Date(announcement.created_at).toLocaleDateString()}</small>
                            </div>
                            <div class="d-flex gap-1">
                                <button class="btn btn-outline-primary btn-sm" onclick="editAnnouncement('${announcement.id}')" title="Edit Announcement">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-outline-danger btn-sm" onclick="deleteAnnouncement('${announcement.id}')" title="Delete Announcement">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        
    } catch (error) {
        console.error('Error loading course announcements:', error);
        document.getElementById('courseAnnouncements').innerHTML = `
            <div class="alert alert-danger alert-sm">Failed to load announcements</div>
        `;
    }
}

function showCreateAnnouncementModal() {
    showAlert('Announcement creation functionality will be implemented with backend integration', 'info');
}

function editAnnouncement(announcementId) {
    showAlert('Announcement editing functionality will be implemented with backend integration', 'info');
}

function deleteAnnouncement(announcementId) {
    if (confirm('Are you sure you want to delete this announcement?')) {
        showAlert('Announcement deleted successfully!', 'success');
        // Refresh announcements tab if we have a current course
        const modal = document.getElementById('teacherCourseModal');
        if (modal && modal.style.display === 'block') {
            const courseId = modal.dataset.courseId;
            if (courseId) {
                loadCourseAnnouncements(courseId);
            }
        }
    }
}

function getFileIcon(fileType) {
    const icons = {
        'pdf': 'pdf',
        'doc': 'word',
        'docx': 'word', 
        'ppt': 'ppt',
        'pptx': 'ppt',
        'jpg': 'image',
        'jpeg': 'image',
        'png': 'image',
        'gif': 'image',
        'zip': 'zip',
        'txt': 'text'
    };
    return icons[fileType] || 'text';
}

function getCategoryBadge(category) {
    const badges = {
        'lecture': '<span class="badge bg-primary">Lecture</span>',
        'assignment': '<span class="badge bg-warning">Assignment</span>',
        'reading': '<span class="badge bg-info">Reading</span>',
        'media': '<span class="badge bg-success">Media</span>',
        'other': '<span class="badge bg-secondary">Other</span>'
    };
    return badges[category] || '<span class="badge bg-secondary">Other</span>';
}



async function refreshImportHistory() {
    await loadImportHistory();
}

async function exportImportErrors(importLogId) {
    try {
        showLoading(true);
        
        // Simulate download
        showAlert('Export functionality will be implemented with backend integration', 'info');
        
    } catch (error) {
        console.error('Error exporting import errors:', error);
        showAlert('Failed to export import errors', 'danger');
    } finally {
        showLoading(false);
    }
}

function logout() {
    // Clear session data
    localStorage.removeItem('authToken');
    sessionStorage.clear();
    
    // Redirect to login
    window.location.href = '/login.html';
}

// Utility functions
function showLoading(show) {
    // This function should be implemented in the main API client
    // For now we'll just log
    console.log('Loading:', show);
}

function showAlert(message, type = 'info') {
    // This function should be implemented in the main API client
    // For now we'll use browser alert
    if (type === 'danger') {
        alert('Error: ' + message);
    } else if (type === 'success') {
        alert('Success: ' + message);
    } else {
        alert(message);
    }
}