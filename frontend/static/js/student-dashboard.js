/*
COMP5241 Group 10 - Student Dashboard JavaScript  
Student interface for course access and materials
*/

// Global variables
let currentUser = null;
let enrolledCourses = [];

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthAndRole('student');
    
    // Initialize dashboard
    initializeStudentDashboard();
    
    // Set up event listeners
    setupEventListeners();
});

function checkAuthAndRole(requiredRole) {
    // This would typically check JWT token and role
    currentUser = {
        id: 'student123',
        username: 'John Doe',
        role: 'student',
        email: 'john.doe@student.edu'
    };
    
    if (currentUser.role !== requiredRole) {
        window.location.href = '/login.html';
        return;
    }
}

function setupEventListeners() {
    // Logout button
    document.getElementById('logoutBtn').addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });
}

async function initializeStudentDashboard() {
    try {
        showLoading(true);
        
        // Load dashboard statistics
        await loadStudentStats();
        
        // Load enrolled courses
        await loadEnrolledCourses();
        
        // Load recent announcements
        await loadRecentAnnouncements();
        
        // Load course progress
        await loadCourseProgress();
        
    } catch (error) {
        console.error('Error initializing student dashboard:', error);
        showAlert('Failed to load dashboard data', 'danger');
    } finally {
        showLoading(false);
    }
}

async function loadStudentStats() {
    try {
        // Mock student statistics
        const stats = {
            enrolled_courses: 3,
            completed_courses: 1,
            average_progress: 68,
            materials_downloaded: 24
        };
        
        // Update UI
        document.getElementById('enrolledCourses').textContent = stats.enrolled_courses;
        document.getElementById('completedCourses').textContent = stats.completed_courses;
        document.getElementById('averageProgress').textContent = stats.average_progress + '%';
        document.getElementById('materialsDownloaded').textContent = stats.materials_downloaded;
        
    } catch (error) {
        console.error('Error loading student stats:', error);
        // Show default values
        document.getElementById('enrolledCourses').textContent = '0';
        document.getElementById('completedCourses').textContent = '0';
        document.getElementById('averageProgress').textContent = '0%';
        document.getElementById('materialsDownloaded').textContent = '0';
    }
}

async function loadEnrolledCourses() {
    try {
        const container = document.getElementById('coursesContainer');
        
        // Mock enrolled courses data
        enrolledCourses = [
            {
                id: '1',
                course: {
                    title: 'Advanced Database Systems',
                    course_code: 'COMP5241',
                    instructor_name: 'Dr. Smith',
                    semester: 'Fall 2025'
                },
                enrollment: {
                    progress_percentage: 75,
                    status: 'enrolled',
                    enrollment_date: '2025-09-15'
                }
            },
            {
                id: '2',
                course: {
                    title: 'Machine Learning Fundamentals',
                    course_code: 'COMP4321',
                    instructor_name: 'Dr. Johnson',
                    semester: 'Fall 2025'
                },
                enrollment: {
                    progress_percentage: 60,
                    status: 'enrolled',
                    enrollment_date: '2025-09-16'
                }
            },
            {
                id: '3',
                course: {
                    title: 'Data Structures',
                    course_code: 'COMP2011',
                    instructor_name: 'Prof. Lee',
                    semester: 'Fall 2025'
                },
                enrollment: {
                    progress_percentage: 100,
                    status: 'completed',
                    enrollment_date: '2025-08-20'
                }
            }
        ];
        
        // Render courses
        container.innerHTML = '';
        if (enrolledCourses.length === 0) {
            container.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-book fs-1"></i>
                    <p>No courses enrolled yet.</p>
                    <a href="student-courses.html" class="btn btn-primary">Browse Available Courses</a>
                </div>
            `;
        } else {
            // Show only first 3 courses on dashboard
            const displayCourses = enrolledCourses.slice(0, 3);
            displayCourses.forEach(courseData => {
                const courseCard = createStudentCourseCard(courseData);
                container.appendChild(courseCard);
            });
            
            if (enrolledCourses.length > 3) {
                const moreCoursesDiv = document.createElement('div');
                moreCoursesDiv.className = 'text-center mt-3';
                moreCoursesDiv.innerHTML = `
                    <a href="student-courses.html" class="btn btn-outline-primary">
                        View All ${enrolledCourses.length} Courses
                    </a>
                `;
                container.appendChild(moreCoursesDiv);
            }
        }
        
    } catch (error) {
        console.error('Error loading enrolled courses:', error);
        document.getElementById('coursesContainer').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> Failed to load courses
            </div>
        `;
    }
}

function createStudentCourseCard(courseData) {
    const card = document.createElement('div');
    card.className = 'card mb-3';
    
    const { course, enrollment } = courseData;
    const statusBadge = getEnrollmentStatusBadge(enrollment.status);
    const progressColor = getProgressColor(enrollment.progress_percentage);
    
    card.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="card-title mb-1">${course.title}</h6>
                    <p class="card-text text-muted mb-2">
                        ${course.course_code} • ${course.instructor_name} • ${course.semester}
                    </p>
                    <div class="mb-2">
                        ${statusBadge}
                    </div>
                    <div class="progress mb-2" style="height: 6px;">
                        <div class="progress-bar ${progressColor}" role="progressbar" 
                             style="width: ${enrollment.progress_percentage}%"></div>
                    </div>
                    <small class="text-muted">${enrollment.progress_percentage}% complete</small>
                </div>
                <div class="text-end">
                    <button class="btn btn-sm btn-primary" onclick="viewStudentCourse('${courseData.id}')">
                        <i class="bi bi-eye"></i> View
                    </button>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

function getEnrollmentStatusBadge(status) {
    const badges = {
        'enrolled': '<span class="badge bg-primary">Enrolled</span>',
        'completed': '<span class="badge bg-success">Completed</span>',
        'dropped': '<span class="badge bg-secondary">Dropped</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
}

function getProgressColor(progress) {
    if (progress >= 80) return 'bg-success';
    if (progress >= 60) return 'bg-info';
    if (progress >= 40) return 'bg-warning';
    return 'bg-danger';
}

async function loadRecentAnnouncements() {
    try {
        const container = document.getElementById('announcementsContainer');
        
        // Mock recent announcements from all courses
        const announcements = [
            {
                id: '1',
                title: 'Assignment 2 Due Date Extended',
                content: 'The due date for Assignment 2 has been extended to next Friday.',
                course_title: 'Advanced Database Systems',
                created_at: '2025-10-06',
                is_urgent: true
            },
            {
                id: '2',
                title: 'Guest Lecture Tomorrow',
                content: 'We will have a guest lecturer from Google tomorrow discussing ML in production.',
                course_title: 'Machine Learning Fundamentals',
                created_at: '2025-10-05',
                is_urgent: false
            },
            {
                id: '3',
                title: 'Office Hours Changed',
                content: 'Office hours have been moved to Wednesdays 2-4 PM.',
                course_title: 'Advanced Database Systems',
                created_at: '2025-10-04',
                is_urgent: false
            }
        ];
        
        container.innerHTML = '';
        if (announcements.length === 0) {
            container.innerHTML = '<p class="text-muted">No recent announcements</p>';
        } else {
            announcements.forEach(announcement => {
                const announcementDiv = document.createElement('div');
                announcementDiv.className = 'mb-3 p-3 border rounded';
                if (announcement.is_urgent) {
                    announcementDiv.classList.add('border-warning');
                }
                
                announcementDiv.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">
                                ${announcement.title}
                                ${announcement.is_urgent ? '<i class="bi bi-exclamation-triangle text-warning"></i>' : ''}
                            </h6>
                            <p class="mb-1">${announcement.content}</p>
                            <small class="text-muted">
                                <i class="bi bi-book"></i> ${announcement.course_title} • 
                                ${new Date(announcement.created_at).toLocaleDateString()}
                            </small>
                        </div>
                    </div>
                `;
                container.appendChild(announcementDiv);
            });
        }
        
    } catch (error) {
        console.error('Error loading recent announcements:', error);
        document.getElementById('announcementsContainer').innerHTML = `
            <div class="alert alert-danger alert-sm">Failed to load announcements</div>
        `;
    }
}

async function loadCourseProgress() {
    try {
        const container = document.getElementById('progressContainer');
        
        if (enrolledCourses.length === 0) {
            container.innerHTML = '<p class="text-muted">No courses to show progress for</p>';
            return;
        }
        
        container.innerHTML = '';
        enrolledCourses.forEach(courseData => {
            const { course, enrollment } = courseData;
            const progressDiv = document.createElement('div');
            progressDiv.className = 'mb-3';
            
            const progressColor = getProgressColor(enrollment.progress_percentage);
            
            progressDiv.innerHTML = `
                <div class="d-flex justify-content-between align-items-center mb-1">
                    <small class="fw-bold">${course.course_code}</small>
                    <small class="text-muted">${enrollment.progress_percentage}%</small>
                </div>
                <div class="progress" style="height: 8px;">
                    <div class="progress-bar ${progressColor}" role="progressbar" 
                         style="width: ${enrollment.progress_percentage}%"></div>
                </div>
            `;
            container.appendChild(progressDiv);
        });
        
    } catch (error) {
        console.error('Error loading course progress:', error);
        document.getElementById('progressContainer').innerHTML = `
            <div class="alert alert-danger alert-sm">Failed to load progress</div>
        `;
    }
}

async function viewStudentCourse(courseId) {
    try {
        // Find the course data
        const courseData = enrolledCourses.find(c => c.id === courseId);
        if (!courseData) {
            showAlert('Course not found', 'danger');
            return;
        }
        
        // Show course details modal
        showStudentCourseModal(courseData);
        
    } catch (error) {
        console.error('Error viewing course:', error);
        showAlert('Failed to load course details', 'danger');
    }
}

function showStudentCourseModal(courseData) {
    const { course, enrollment } = courseData;
    
    // Set modal title
    document.getElementById('courseDetailsTitle').textContent = course.title;
    
    // Populate overview tab
    document.getElementById('courseOverview').innerHTML = `
        <div class="row">
            <div class="col-md-8">
                <h6>Course Information</h6>
                <table class="table table-borderless">
                    <tr><td><strong>Code:</strong></td><td>${course.course_code}</td></tr>
                    <tr><td><strong>Instructor:</strong></td><td>${course.instructor_name}</td></tr>
                    <tr><td><strong>Semester:</strong></td><td>${course.semester}</td></tr>
                </table>
                
                <h6>My Progress</h6>
                <div class="progress mb-2" style="height: 20px;">
                    <div class="progress-bar ${getProgressColor(enrollment.progress_percentage)}" 
                         role="progressbar" style="width: ${enrollment.progress_percentage}%">
                        ${enrollment.progress_percentage}%
                    </div>
                </div>
                <p>Status: ${getEnrollmentStatusBadge(enrollment.status)}</p>
                <p><small class="text-muted">Enrolled: ${new Date(enrollment.enrollment_date).toLocaleDateString()}</small></p>
            </div>
            <div class="col-md-4">
                <h6>Quick Actions</h6>
                <div class="d-grid gap-2">
                    <button class="btn btn-outline-primary btn-sm" onclick="viewCourseMaterials('${courseData.id}')">
                        <i class="bi bi-files"></i> View Materials
                    </button>
                    <button class="btn btn-outline-info btn-sm" onclick="viewCourseAnnouncements('${courseData.id}')">
                        <i class="bi bi-megaphone"></i> Announcements
                    </button>
                </div>
            </div>
        </div>
    `;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('courseDetailsModal'));
    modal.show();
    
    // Set up tab event listeners
    document.getElementById('materials-tab').addEventListener('click', () => loadStudentCourseMaterials(courseData.id));
    document.getElementById('announcements-tab').addEventListener('click', () => loadStudentCourseAnnouncements(courseData.id));
}

async function loadStudentCourseMaterials(courseId) {
    try {
        const container = document.getElementById('courseMaterials');
        container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div></div>';
        
        // Mock materials data (only published materials for students)
        const materials = [
            {
                id: '1',
                title: 'Lecture 1 - Introduction to Database Systems',
                file_name: 'lecture1.pdf',
                file_type: 'pdf',
                file_size: 2048576, // bytes
                uploaded_at: '2025-09-10',
                category: 'lecture'
            },
            {
                id: '2',
                title: 'Assignment 1 - ER Modeling',
                file_name: 'assignment1.docx',
                file_type: 'docx',
                file_size: 1048576,
                uploaded_at: '2025-09-15',
                category: 'assignment'
            },
            {
                id: '3',
                title: 'Lab Exercise 1',
                file_name: 'lab1.zip',
                file_type: 'zip',
                file_size: 5242880,
                uploaded_at: '2025-09-20',
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
                                    ${material.file_name} • ${formatFileSize(material.file_size)} • 
                                    ${getCategoryBadge(material.category)}
                                </small>
                                <br>
                                <small class="text-muted">Uploaded: ${new Date(material.uploaded_at).toLocaleDateString()}</small>
                            </div>
                            <div>
                                <button class="btn btn-sm btn-primary" onclick="downloadMaterial('${material.id}')">
                                    <i class="bi bi-download"></i> Download
                                </button>
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

async function loadStudentCourseAnnouncements(courseId) {
    try {
        const container = document.getElementById('courseAnnouncements');
        container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div></div>';
        
        // Mock announcements data for this specific course
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

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
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

// Action functions
function viewCourseMaterials(courseId) {
    // Switch to materials tab
    document.getElementById('materials-tab').click();
}

function viewCourseAnnouncements(courseId) {
    // Switch to announcements tab  
    document.getElementById('announcements-tab').click();
}

async function downloadMaterial(materialId) {
    try {
        showLoading(true);
        
        // Simulate download - in real app, this would be an API call
        showAlert('Download started! (This is a simulation)', 'success');
        
        // In real implementation:
        // const response = await CoursesAPI.downloadMaterial(materialId);
        // if (response.success) {
        //     // Trigger file download
        //     window.open(response.download_url, '_blank');
        // }
        
    } catch (error) {
        console.error('Error downloading material:', error);
        showAlert('Failed to download material', 'danger');
    } finally {
        showLoading(false);
    }
}

async function refreshDashboard() {
    await initializeStudentDashboard();
    showAlert('Dashboard refreshed!', 'success');
}

function logout() {
    localStorage.removeItem('authToken');
    sessionStorage.clear();
    window.location.href = '/login.html';
}

// Utility functions
function showLoading(show) {
    console.log('Loading:', show);
}

function showAlert(message, type = 'info') {
    if (type === 'danger') {
        alert('Error: ' + message);
    } else if (type === 'success') {
        alert('Success: ' + message);
    } else {
        alert(message);
    }
}