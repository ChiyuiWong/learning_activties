/*
COMP5241 Group 10 - Authentication Module
Sunny's responsibility for security implementation
*/

// Authentication manager
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.token = localStorage.getItem('authToken');
        this.initializeAuth();
    }
    
    // Initialize authentication state
    initializeAuth() {
        if (this.token) {
            this.validateToken();
        }
    }
    
    // Validate stored token
    async validateToken() {
        try {
            const response = await SecurityAPI.getProfile();
            this.currentUser = response.user;
            this.updateUI();
        } catch (error) {
            console.warn('Token validation failed:', error.message);
            this.logout();
        }
    }

    
    // Register new user
    async register(userData) {
        try {
            const response = await SecurityAPI.register(userData);
            showAlert('Registration successful! Please login.', 'success');
            return true;
        } catch (error) {
            showAlert('Registration failed: ' + error.message, 'danger');
            return false;
        }
    }
    
    // Logout user
    async logout() {
        try {
            if (this.token) {
                await SecurityAPI.logout();
            }
        } catch (error) {
            console.warn('Logout API call failed:', error.message);
        } finally {
            // Clear local state
            this.token = null;
            this.currentUser = null;
            
            // Clear stored token
            if (api.setToken) {
                api.setToken(null);
            } else {
                localStorage.removeItem('authToken');
                api.token = null;
                console.log('Token cleared from localStorage');
            }
            
            // Update UI
            if (typeof this.updateUI === 'function') {
                this.updateUI();
            }
            
            // Show login modal if the function exists
            if (typeof showLoginModal === 'function') {
                showLoginModal();
            }
            
            // Show alert if the function exists
            if (typeof showAlert === 'function') {
                showAlert('You have been logged out.', 'info');
            }
        }
    }
    
    // Update UI based on authentication state
    updateUI() {
        const userNameElement = document.getElementById('user-name');
        const mainContent = document.getElementById('main-content');
        
        if (this.currentUser) {
            // User is logged in
            if (userNameElement) {
                userNameElement.textContent = this.currentUser.first_name || this.currentUser.username;
            }
            
            // Show/hide navigation items based on role
            this.updateNavigationByRole();
            
            // Show main content
            if (mainContent) {
                mainContent.style.display = 'block';
            }
        } else {
            // User is not logged in
            if (userNameElement) {
                userNameElement.textContent = 'Guest';
            }
            
            // Hide main content
            if (mainContent) {
                mainContent.style.display = 'none';
            }
        }
    }
    
    // Update navigation based on user role
    updateNavigationByRole() {
        if (!this.currentUser) return;
        
        const role = this.currentUser.role;
        
        // Admin section visibility
        const adminNavItems = document.querySelectorAll('[data-section="admin"]');
        adminNavItems.forEach(item => {
            if (role === 'admin') {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        // Teacher-specific features
        const teacherFeatures = document.querySelectorAll('.teacher-only');
        teacherFeatures.forEach(item => {
            if (role === 'teacher' || role === 'admin') {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
        
        // Student-specific features
        const studentFeatures = document.querySelectorAll('.student-only');
        studentFeatures.forEach(item => {
            if (role === 'student') {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }
    
    // Check if user has specific role
    hasRole(role) {
        return this.currentUser && this.currentUser.role === role;
    }
    
    // Check if user is admin
    isAdmin() {
        return this.hasRole('admin');
    }
    
    // Check if user is teacher
    isTeacher() {
        return this.hasRole('teacher') || this.isAdmin();
    }
    
    // Check if user is student
    isStudent() {
        return this.hasRole('student');
    }
    
    // Get current user
    getCurrentUser() {
        return this.currentUser;
    }
    
    // Get current user ID
    getCurrentUserId() {
        return this.currentUser ? this.currentUser.id : null;
    }
    
    // Check if user is authenticated
    isAuthenticated() {
        return !!this.token && !!this.currentUser;
    }
}

// Create global auth manager instance
const auth = new AuthManager();

// Enhanced login form handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value;
            
            if (!username || !password) {
                showAlert('Please enter both username and password.', 'warning');
                return;
            }
            
            // Disable form during login
            const submitBtn = loginForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Logging in...';
            
            try {
                const success = await auth.login(username, password);
                if (success) {
                    loginForm.reset();
                }
            } finally {
                // Re-enable form
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        });
    }
    
    // Enhanced logout handler
    const logoutBtn = document.getElementById('nav-logout');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async function(e) {
            e.preventDefault();
            await auth.logout();
        });
    }
});

// Role-based route protection
function requireAuth() {
    if (!auth.isAuthenticated()) {
        showLoginModal();
        return false;
    }
    return true;
}

function requireRole(role) {
    if (!requireAuth()) return false;
    
    if (!auth.hasRole(role)) {
        showAlert(`Access denied. ${role} role required.`, 'danger');
        return false;
    }
    return true;
}

function requireAdmin() {
    return requireRole('admin');
}

function requireTeacher() {
    if (!requireAuth()) return false;
    
    if (!auth.isTeacher()) {
        showAlert('Access denied. Teacher or admin role required.', 'danger');
        return false;
    }
    return true;
}

// Auto-logout on token expiration
setInterval(async () => {
    if (auth.isAuthenticated()) {
        try {
            await auth.validateToken();
        } catch (error) {
            console.warn('Token validation failed, logging out...');
            await auth.logout();
        }
    }
}, 300000); // Check every 5 minutes

// Export auth manager and utilities
window.auth = auth;
window.requireAuth = requireAuth;
window.requireRole = requireRole;
window.requireAdmin = requireAdmin;
window.requireTeacher = requireTeacher;

// TODO for Sunny: Implement the following features
// 1. Password strength validation
// 2. Two-factor authentication
// 3. Session management
// 4. Password reset functionality
// 5. Account verification
// 6. Security audit logging
// 7. Rate limiting for login attempts
// 8. CSRF protection
// 9. Secure password hashing (backend)
// 10. JWT token refresh mechanism
