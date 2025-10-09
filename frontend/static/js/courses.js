/*
COMP5241 Group 10 - Course Management JavaScript
Enhanced course management and teacher tools functionality
*/

// Global variables
let currentUser = null;
let currentCourseId = null;
let currentPage = 1;
let totalPages = 1;

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuthAndRole('teacher');
    
    // Initialize page
    initializeCoursesPage();
    
    // Set up event listeners
    setupEventListeners();
});

function checkAuthAndRole(requiredRole) {
    // This would typically check JWT token and role
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
    
    // Import students form
    document.getElementById('importStudentsForm').addEventListener('submit', handleImportStudents);
    
    // Search input
    document.getElementById('searchCourses').addEventListener('input', debounce(applyCourseFilters, 500));
    
    // Logout button  
    document.getElementById('logoutBtn').addEventListener('click', function(e) {
        e.preventDefault();
        logout();
    });
}

async function initializeCoursesPage() {
    try {
        showLoading(true);
        
        // Load filter options
        await loadFilterOptions();
        
        // Load courses
        await loadCourses();
        
    } catch (error) {
        console.error('Error initializing courses page:', error);
        showAlert('Failed to load courses data', 'danger');
    } finally {
        showLoading(false);
    }
}

async function loadFilterOptions() {
    try {
        // Mock filter options - in real app, get from API
        const categories = ['Computer Science', 'Mathematics', 'Engineering', 'Business'];
        const semesters = ['Fall 2025', 'Spring 2026', 'Summer 2026'];
        
        // Populate category filter
        const categorySelect = document.getElementById('filterCategory');
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categorySelect.appendChild(option);
        });
        
        // Populate semester filter
        const semesterSelect = document.getElementById('filterSemester');
        semesters.forEach(semester => {
            const option = document.createElement('option');
            option.value = semester;
            option.textContent = semester; 
            semesterSelect.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading filter options:', error);
    }
}

async function loadCourses(page = 1) {
    try {
        const container = document.getElementById('coursesContainer');
        container.innerHTML = '<div class="text-center"><div class="spinner-border" role="status"></div></div>';
        
        // Get filter values
        const filters = getActiveFilters();
        
        // Simulate API call
        // const response = await CoursesAPI.getCourses({ page, per_page: 10, ...filters });
        
        // Mock data
        const mockResponse = {
            success: true,
            courses: [
                {
                    id: '1',
                    title: 'Advanced Database Systems',
                    course_code: 'COMP5241',
                    description: 'Advanced topics in database systems including distributed databases, NoSQL, and performance optimization.',
                    category: 'Computer Science',
                    difficulty_level: 'advanced',
                    current_enrollment: 45,
                    max_students: 50,
                    is_published: true,
                    is_active: true,
                    semester: 'Fall 2025',
                    university: 'PolyU',
                    created_at: '2025-09-01'
                },
                {
                    id: '2',
                    title: 'Machine Learning Fundamentals',
                    course_code: 'COMP4321',
                    description: 'Introduction to machine learning algorithms and applications.',
                    category: 'Computer Science',
                    difficulty_level: 'intermediate',
                    current_enrollment: 38,
                    max_students: 40,
                    is_published: true,
                    is_active: true,
                    semester: 'Fall 2025',
                    university: 'PolyU',
                    created_at: '2025-09-01'
                },
                {
                    id: '3',
                    title: 'Web Development',
                    course_code: 'COMP3421',
                    description: 'Full-stack web development using modern frameworks.',
                    category: 'Computer Science',
                    difficulty_level: 'beginner',
                    current_enrollment: 25,
                    max_students: 30,
                    is_published: false,
                    is_active: true,
                    semester: 'Spring 2026',
                    university: 'PolyU',
                    created_at: '2025-10-01'
                }
            ],
            pagination: {
                page: 1,
                per_page: 10,
                total: 3,
                pages: 1
            }
        };
        
        if (mockResponse.success) {
            renderCourses(mockResponse.courses);
            renderPagination(mockResponse.pagination);
        } else {
            container.innerHTML = `
                <div class="alert alert-danger">
                    <i class="bi bi-exclamation-triangle"></i> Failed to load courses
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading courses:', error);
        document.getElementById('coursesContainer').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> Error loading courses
            </div>
        `;
    }
}

function getActiveFilters() {
    return {
        category: document.getElementById('filterCategory').value,
        semester: document.getElementById('filterSemester').value,
        search: document.getElementById('searchCourses').value.trim()
    };
}

function renderCourses(courses) {
    const container = document.getElementById('coursesContainer');
    
    if (courses.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted py-5">
                <i class="bi bi-book fs-1"></i>
                <h5>No courses found</h5>
                <p>Try adjusting your filters or create a new course.</p>
                <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#createCourseModal">
                    <i class="bi bi-plus-circle"></i> Create Course
                </button>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '';
    courses.forEach(course => {
        const courseCard = createAdvancedCourseCard(course);
        container.appendChild(courseCard);
    });
}

function createAdvancedCourseCard(course) {
    const card = document.createElement('div');
    card.className = 'card mb-4';
    
    const progressPercentage = Math.round((course.current_enrollment / course.max_students) * 100);
    const statusBadge = getStatusBadge(course);
    const difficultyBadge = getDifficultyBadge(course.difficulty_level);
    
    card.innerHTML = `
        <div class="card-body">
            <div class="row">
                <div class="col-md-8">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <h5 class="card-title mb-1">${course.title}</h5>
                            <p class="text-muted mb-1">${course.course_code} • ${course.semester}</p>
                            <div class="mb-2">
                                ${statusBadge}
                                ${difficultyBadge}
                                <span class="badge bg-light text-dark">${course.category}</span>
                            </div>
                        </div>
                    </div>
                    <p class="card-text">${course.description}</p>
                    <div class="row text-muted small">
                        <div class="col-md-6">
                            <i class="bi bi-people"></i> ${course.current_enrollment}/${course.max_students} students
                        </div>
                        <div class="col-md-6">
                            <i class="bi bi-building"></i> ${course.university}
                        </div>
                    </div>
                </div>
                <div class="col-md-4 text-end">
                    <div class="mb-3">
                        <div class="progress mb-1" style="height: 8px;">
                            <div class="progress-bar" role="progressbar" style="width: ${progressPercentage}%"></div>
                        </div>
                        <small class="text-muted">${progressPercentage}% capacity</small>
                    </div>
                    <div class="btn-group-vertical d-grid gap-1">
                        <button class="btn btn-primary btn-sm" onclick="viewCourseDetails('${course.id}')">
                            <i class="bi bi-eye"></i> View Details
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" onclick="manageCourse('${course.id}')">
                            <i class="bi bi-gear"></i> Manage
                        </button>
                        ${course.is_published ? 
                            `<button class="btn btn-outline-warning btn-sm" onclick="toggleCourseStatus('${course.id}', false)">
                                <i class="bi bi-eye-slash"></i> Unpublish
                            </button>` :
                            `<button class="btn btn-outline-success btn-sm" onclick="toggleCourseStatus('${course.id}', true)">
                                <i class="bi bi-eye"></i> Publish
                            </button>`
                        }
                    </div>
                </div>
            </div>
        </div>
    `;
    
    return card;
}

function getStatusBadge(course) {
    if (course.is_published && course.is_active) {
        return '<span class="badge bg-success">Published</span>';
    } else if (!course.is_published && course.is_active) {
        return '<span class="badge bg-warning">Draft</span>';
    } else {
        return '<span class="badge bg-secondary">Inactive</span>';
    }
}

function getDifficultyBadge(difficulty) {
    const badges = {
        'beginner': '<span class="badge bg-info">Beginner</span>',
        'intermediate': '<span class="badge bg-warning">Intermediate</span>',
        'advanced': '<span class="badge bg-danger">Advanced</span>'
    };
    return badges[difficulty] || '<span class="badge bg-secondary">Unknown</span>';
}

function renderPagination(pagination) {
    const container = document.getElementById('coursesPagination');
    container.innerHTML = '';
    
    if (pagination.pages <= 1) return;
    
    currentPage = pagination.page;
    totalPages = pagination.pages;
    
    // Previous button
    const prevLi = document.createElement('li');
    prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
    prevLi.innerHTML = `
        <a class="page-link" href="#" onclick="changePage(${currentPage - 1})">
            <i class="bi bi-chevron-left"></i>
        </a>
    `;
    container.appendChild(prevLi);
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
            pageLi.innerHTML = `
                <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
            `;
            container.appendChild(pageLi);
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            const ellipsisLi = document.createElement('li');
            ellipsisLi.className = 'page-item disabled';
            ellipsisLi.innerHTML = '<span class="page-link">...</span>';
            container.appendChild(ellipsisLi);
        }
    }
    
    // Next button
    const nextLi = document.createElement('li');
    nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
    nextLi.innerHTML = `
        <a class="page-link" href="#" onclick="changePage(${currentPage + 1})">
            <i class="bi bi-chevron-right"></i>
        </a>
    `;
    container.appendChild(nextLi);
}

async function viewCourseDetails(courseId) {
    try {
        currentCourseId = courseId;
        
        // Load course details
        // const response = await CoursesAPI.getCourse(courseId, { include_stats: true });
        
        // Mock data
        const mockCourse = {
            id: courseId,
            title: 'Advanced Database Systems',
            course_code: 'COMP5241',
            description: 'Advanced topics in database systems including distributed databases, NoSQL, and performance optimization.',
            category: 'Computer Science',
            difficulty_level: 'advanced',
            current_enrollment: 45,
            max_students: 50,
            is_published: true,
            semester: 'Fall 2025',
            university: 'PolyU',
            instructor_name: 'Dr. Smith',
            stats: {
                total_enrolled: 45,
                active_students: 43,
                completed: 2,
                materials_count: 8,
                announcements_count: 3
            }
        };
        
        // Show modal
        showCourseDetailsModal(mockCourse);
        
    } catch (error) {
        console.error('Error loading course details:', error);
        showAlert('Failed to load course details', 'danger');
    }
}

function showCourseDetailsModal(course) {
    // Set modal title
    document.getElementById('courseDetailsTitle').textContent = course.title;
    
    // Populate overview tab
    document.getElementById('courseOverview').innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6>Course Information</h6>
                <table class="table table-borderless">
                    <tr><td><strong>Code:</strong></td><td>${course.course_code}</td></tr>
                    <tr><td><strong>Category:</strong></td><td>${course.category}</td></tr>
                    <tr><td><strong>Difficulty:</strong></td><td>${course.difficulty_level}</td></tr>
                    <tr><td><strong>Semester:</strong></td><td>${course.semester}</td></tr>
                    <tr><td><strong>University:</strong></td><td>${course.university}</td></tr>
                    <tr><td><strong>Instructor:</strong></td><td>${course.instructor_name}</td></tr>
                </table>
            </div>
            <div class="col-md-6">
                <h6>Statistics</h6>
                <div class="row">
                    <div class="col-6">
                        <div class="card text-center">
                            <div class="card-body p-2">
                                <h4 class="text-primary">${course.stats.total_enrolled}</h4>
                                <small>Total Students</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="card text-center">
                            <div class="card-body p-2">
                                <h4 class="text-success">${course.stats.materials_count}</h4>
                                <small>Materials</small>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="mt-3">
            <h6>Description</h6>
            <p>${course.description}</p>
        </div>
    `;
    
    // Show the modal
    const modal = new bootstrap.Modal(document.getElementById('courseDetailsModal'));
    modal.show();
    
    // Load additional tabs when clicked
    document.getElementById('students-tab').addEventListener('click', () => loadCourseStudents(course.id));
    document.getElementById('materials-tab').addEventListener('click', () => loadCourseMaterials(course.id));
    document.getElementById('announcements-tab').addEventListener('click', () => loadCourseAnnouncements(course.id));
}

async function loadCourseStudents(courseId) {
    try {
        const container = document.getElementById('courseStudents');
        container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div></div>';
        
        // Mock students data
        const students = [
            { id: '1', student_name: 'John Doe', student_email: 'john@student.edu', enrollment_date: '2025-09-15', status: 'enrolled', progress_percentage: 75 },
            { id: '2', student_name: 'Sarah Smith', student_email: 'sarah@student.edu', enrollment_date: '2025-09-16', status: 'enrolled', progress_percentage: 85 }
        ];
        
        container.innerHTML = `
            <div class="table-responsive">
                <table class="table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Email</th>
                            <th>Enrolled</th>
                            <th>Progress</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${students.map(student => `
                            <tr>
                                <td>${student.student_name}</td>
                                <td>${student.student_email}</td>
                                <td><small>${new Date(student.enrollment_date).toLocaleDateString()}</small></td>
                                <td>
                                    <div class="progress" style="height: 15px;">
                                        <div class="progress-bar" style="width: ${student.progress_percentage}%">
                                            ${student.progress_percentage}%
                                        </div>
                                    </div>
                                </td>
                                <td><span class="badge bg-success">${student.status}</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
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
            { id: '1', title: 'Lecture 1 - Introduction', file_name: 'lecture1.pdf', file_type: 'pdf', uploaded_at: '2025-09-10', download_count: 42 },
            { id: '2', title: 'Assignment 1', file_name: 'assignment1.docx', file_type: 'docx', uploaded_at: '2025-09-15', download_count: 38 }
        ];
        
        container.innerHTML = `
            <div class="list-group">
                ${materials.map(material => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h6 class="mb-1">${material.title}</h6>
                                <small class="text-muted">
                                    <i class="bi bi-file-earmark-${getFileIcon(material.file_type)}"></i> 
                                    ${material.file_name} • Downloaded ${material.download_count} times
                                </small>
                            </div>
                            <div>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteMaterial('${material.id}')">
                                    <i class="bi bi-trash"></i>
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

async function loadCourseAnnouncements(courseId) {
    try {
        const container = document.getElementById('courseAnnouncements');
        container.innerHTML = '<div class="text-center"><div class="spinner-border spinner-border-sm"></div></div>';
        
        // Mock announcements data
        const announcements = [
            { id: '1', title: 'Welcome to the course!', content: 'Welcome everyone to Advanced Database Systems...', created_at: '2025-09-01', is_pinned: true },
            { id: '2', title: 'Assignment 1 Due Date', content: 'Please note that Assignment 1 is due next Friday...', created_at: '2025-09-15', is_pinned: false }
        ];
        
        container.innerHTML = `
            <div class="list-group">
                ${announcements.map(announcement => `
                    <div class="list-group-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div>
                                <h6 class="mb-1">
                                    ${announcement.title}
                                    ${announcement.is_pinned ? '<i class="bi bi-pin-angle text-warning"></i>' : ''}
                                </h6>
                                <p class="mb-1">${announcement.content}</p>
                                <small class="text-muted">${new Date(announcement.created_at).toLocaleDateString()}</small>
                            </div>
                            <div>
                                <button class="btn btn-sm btn-outline-primary" onclick="editAnnouncement('${announcement.id}')">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteAnnouncement('${announcement.id}')">
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
        'gif': 'image'
    };
    return icons[fileType] || 'text';
}

// Event handlers
async function handleCreateCourse(event) {
    event.preventDefault();
    
    try {
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
        
        showLoading(true);
        
        // Mock success
        showAlert('Course created successfully!', 'success');
        
        // Close modal and refresh
        const modal = bootstrap.Modal.getInstance(document.getElementById('createCourseModal'));
        modal.hide();
        event.target.reset();
        await loadCourses();
        
    } catch (error) {
        console.error('Error creating course:', error);
        showAlert('Failed to create course', 'danger');
    } finally {
        showLoading(false);
    }
}

async function handleImportStudents(event) {
    event.preventDefault();
    
    try {
        const fileInput = document.getElementById('csvFile');
        const file = fileInput.files[0];
        
        if (!file) {
            showAlert('Please select a CSV file', 'danger');
            return;
        }
        
        if (!currentCourseId) {
            showAlert('No course selected', 'danger');
            return;
        }
        
        showLoading(true);
        
        // Mock import process
        setTimeout(() => {
            showAlert('Students imported successfully! 45 students added, 2 duplicates skipped.', 'success');
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('importStudentsModal'));
            modal.hide();
            
            // Refresh students tab if open
            if (document.getElementById('students-tab').classList.contains('active')) {
                loadCourseStudents(currentCourseId);
            }
            
            showLoading(false);
        }, 2000);
        
    } catch (error) {
        console.error('Error importing students:', error);
        showAlert('Failed to import students', 'danger');
        showLoading(false);
    }
}

// Filter and search functions
function applyCourseFilters() {
    loadCourses(1);
}

function clearCourseFilters() {
    document.getElementById('filterCategory').value = '';
    document.getElementById('filterSemester').value = '';
    document.getElementById('filterStatus').value = '';
    document.getElementById('searchCourses').value = '';
    loadCourses(1);
}

function refreshCourses() {
    loadCourses(currentPage);
}

function changePage(page) {
    if (page >= 1 && page <= totalPages && page !== currentPage) {
        loadCourses(page);
    }
}

// Course management functions
function manageCourse(courseId) {
    // Open course management interface
    viewCourseDetails(courseId);
}

async function toggleCourseStatus(courseId, publish) {
    try {
        showLoading(true);
        
        // Mock API call
        const action = publish ? 'published' : 'unpublished';
        showAlert(`Course ${action} successfully!`, 'success');
        
        // Refresh courses
        await loadCourses(currentPage);
        
    } catch (error) {
        console.error('Error toggling course status:', error);
        showAlert('Failed to update course status', 'danger');
    } finally {
        showLoading(false);
    }
}

function showImportStudentsModal() {
    const modal = new bootstrap.Modal(document.getElementById('importStudentsModal'));
    modal.show();
}

function exportStudents() {
    if (!currentCourseId) {
        showAlert('No course selected', 'danger');
        return;
    }
    
    // Mock export
    showAlert('Export functionality will be implemented with backend integration', 'info');
}

function showUploadMaterialModal() {
    showAlert('Material upload functionality will be implemented with backend integration', 'info');
}

function showCreateAnnouncementModal() {
    showAlert('Announcement creation functionality will be implemented with backend integration', 'info');
}

function deleteMaterial(materialId) {
    if (confirm('Are you sure you want to delete this material?')) {
        showAlert('Material deleted successfully!', 'success');
        // Refresh materials tab
        if (currentCourseId) {
            loadCourseMaterials(currentCourseId);
        }
    }
}

function editAnnouncement(announcementId) {
    showAlert('Announcement editing functionality will be implemented with backend integration', 'info');
}

function deleteAnnouncement(announcementId) {
    if (confirm('Are you sure you want to delete this announcement?')) {
        showAlert('Announcement deleted successfully!', 'success');
        // Refresh announcements tab
        if (currentCourseId) {
            loadCourseAnnouncements(currentCourseId);
        }
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function logout() {
    localStorage.removeItem('authToken');
    sessionStorage.clear();
    window.location.href = '/login.html';
}

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