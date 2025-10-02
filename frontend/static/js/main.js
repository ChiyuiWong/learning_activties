/*
COMP5241 Group 10 - Main JavaScript
Joyce's responsibility for UI functionality
*/

// Global application state
const app = {
    currentUser: null,
    currentSection: 'dashboard',
    apiBaseUrl: 'http://localhost:5000/api'
};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    bindEventListeners();
    showSection('dashboard');
});

// Initialize application
function initializeApp() {
    console.log('Initializing COMP5241 LMS Application...');
    
    // Check if user is logged in
    const token = localStorage.getItem('authToken');
    const userInfo = localStorage.getItem('userInfo');
    
    if (token && userInfo) {
        try {
            app.currentUser = JSON.parse(userInfo);
            console.log('User logged in:', app.currentUser);
            
            // Update UI with user info
            updateUserInterface();
            
            // Initialize learning activities with user role
            if (typeof learningActivities !== 'undefined') {
                setTimeout(() => {
                    learningActivities.setUserRole(app.currentUser.role);
                }, 500);
            }
            
        } catch (error) {
            console.error('Error parsing user info:', error);
            redirectToLogin();
            return;
        }
    } else {
        // Redirect to login page
        redirectToLogin();
        return;
    }
    
    // Initialize modules
    initializeGenAI();
    initializeSecurity();
    initializeCourses();
    initializeActivities();
    initializeAdmin();
}

function updateUserInterface() {
    // Update user name in navbar
    const userNameEl = document.getElementById('user-name');
    if (userNameEl && app.currentUser) {
        userNameEl.textContent = app.currentUser.username;
    }
    
    // Show/hide teacher-specific features
    const teacherElements = document.querySelectorAll('[data-role="teacher"]');
    teacherElements.forEach(el => {
        if (app.currentUser && app.currentUser.role === 'teacher') {
            el.style.display = '';
        } else {
            el.style.display = 'none';
        }
    });
}

function redirectToLogin() {
    // Only redirect if not already on login page
    if (!window.location.pathname.includes('login.html')) {
        window.location.href = '/login.html';
    }
}

// Bind event listeners
function bindEventListeners() {
    // Navigation
    document.querySelectorAll('[data-section]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('data-section');
            showSection(section);
        });
    });
    
    // Login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // Logout
    const logoutBtn = document.getElementById('nav-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // GenAI features (Ting's module)
    const generateBtn = document.getElementById('generate-ai-content');
    if (generateBtn) {
        generateBtn.addEventListener('click', handleGenAIGeneration);
    }
    
    // Course features (Keith's module)
    const createCourseBtn = document.getElementById('create-course-btn');
    if (createCourseBtn) {
        createCourseBtn.addEventListener('click', handleCreateCourse);
    }
    
    // Activity features (Charlie's module)
    const createActivityBtn = document.getElementById('create-activity-btn');
    if (createActivityBtn) {
        createActivityBtn.addEventListener('click', handleCreateActivity);
    }
}

// Show specific section
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.add('d-none');
    });
    
    // Show target section
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.classList.remove('d-none');
        app.currentSection = sectionName;
        
        // Update active navigation
        updateActiveNavigation(sectionName);
        
        // Load section data
        loadSectionData(sectionName);
    }
}

// Update active navigation
function updateActiveNavigation(sectionName) {
    document.querySelectorAll('[data-section]').forEach(link => {
        link.classList.remove('active');
    });
    
    document.querySelectorAll(`[data-section="${sectionName}"]`).forEach(link => {
        link.classList.add('active');
    });
}

// Load data for specific section
function loadSectionData(sectionName) {
    switch(sectionName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'courses':
            loadCoursesData();
            break;
        case 'activities':
            loadActivitiesData();
            break;
        case 'genai':
            loadGenAIData();
            break;
        case 'admin':
            loadAdminData();
            break;
    }
}

// Dashboard data loading
function loadDashboardData() {
    console.log('Loading dashboard data...');
    
    // Load quick stats
    loadQuickStats();
}

function loadQuickStats() {
    // These will be implemented by respective team members
    document.getElementById('enrolled-courses-count').textContent = 'Loading...';
    document.getElementById('pending-activities-count').textContent = 'Loading...';
    document.getElementById('completed-activities-count').textContent = 'Loading...';
    
    // Placeholder API calls
    // Keith will implement course counting
    // Charlie will implement activity counting
}

// Courses data loading (Keith's responsibility)
function loadCoursesData() {
    console.log('Loading courses data... (Keith to implement)');
    const coursesList = document.getElementById('courses-list');
    if (coursesList) {
        coursesList.innerHTML = '<div class="alert alert-info">Courses module to be implemented by Keith</div>';
    }
}

// Activities data loading (Charlie's responsibility)
function loadActivitiesData() {
    console.log('Loading activities data... (Charlie to implement)');
    const activitiesList = document.getElementById('activities-list');
    if (activitiesList) {
        activitiesList.innerHTML = '<div class="alert alert-info">Learning Activities module to be implemented by Charlie</div>';
    }
}

// GenAI data loading (Ting's responsibility)
function loadGenAIData() {
    console.log('Loading GenAI data...');
    if (typeof GenAI !== 'undefined') {
        GenAI.init();
    }
}

// Admin data loading (Sunny's responsibility)
function loadAdminData() {
    console.log('Loading admin data... (Sunny to implement)');
}

// Initialize module-specific functionality
function initializeGenAI() {
    console.log('Initializing GenAI module...');
    // GenAI will be initialized when the section is loaded
}

function initializeSecurity() {
    console.log('Initializing Security module... (Sunny to implement)');
}

function initializeCourses() {
    console.log('Initializing Courses module... (Keith to implement)');
}

function initializeActivities() {
    console.log('Initializing Activities module... (Charlie to implement)');
}

function initializeAdmin() {
    console.log('Initializing Admin module... (Sunny to implement)');
}

// Event handlers
function handleLogin(e) {
    e.preventDefault();
    console.log('Handling login... (Sunny to implement)');
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    // Placeholder - Sunny will implement actual authentication
    showAlert('Login functionality to be implemented by Sunny', 'info');
}

function handleLogout(e) {
    e.preventDefault();
    console.log('Logging out user...');
    
    // Clear local storage
    localStorage.removeItem('authToken');
    localStorage.removeItem('userInfo');
    
    // Clear current user
    app.currentUser = null;
    
    // Show success message and redirect
    showNotification('Logged out successfully!', 'success');
    
    setTimeout(() => {
        window.location.href = '/login.html';
    }, 1000);
}

function handleGenAIGeneration(e) {
    e.preventDefault();
    console.log('Handling GenAI generation... (Ting to implement)');
    
    const prompt = document.getElementById('ai-prompt').value;
    const resultDiv = document.getElementById('ai-result');
    
    if (prompt.trim()) {
        resultDiv.innerHTML = '<div class="alert alert-info">GenAI generation to be implemented by Ting</div>';
    } else {
        showAlert('Please enter a prompt', 'warning');
    }
}

function handleCreateCourse(e) {
    e.preventDefault();
    console.log('Handling course creation... (Keith to implement)');
    showAlert('Course creation to be implemented by Keith', 'info');
}

function handleCreateActivity(e) {
    e.preventDefault();
    console.log('Handling activity creation... (Charlie to implement)');
    showAlert('Activity creation to be implemented by Charlie', 'info');
}

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 3000);
}

function showLoginModal() {
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
}

function validateToken(token) {
    // Sunny will implement token validation
    console.log('Validating token... (Sunny to implement)');
}

function showLoading(show = true) {
    let loadingOverlay = document.getElementById('loading-overlay');
    
    if (show) {
        if (!loadingOverlay) {
            loadingOverlay = document.createElement('div');
            loadingOverlay.id = 'loading-overlay';
            loadingOverlay.className = 'loading-overlay';
            loadingOverlay.innerHTML = '<div class="loading-spinner"></div>';
            document.body.appendChild(loadingOverlay);
        }
        loadingOverlay.style.display = 'flex';
    } else {
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
}

// Export functions for module use
window.app = app;
window.showAlert = showAlert;
window.showLoading = showLoading;
window.showSection = showSection;
