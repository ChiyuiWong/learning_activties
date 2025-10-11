/*
 * Auth Helpers - Simple authentication utility functions for test pages
 */

// Simple function to check if user is authenticated
function checkAuth() {
    // Look for auth token or user in localStorage
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    
    // If either is missing, try auto-login
    if (!token || !user) {
        // For testing convenience, create a default teacher account
        const createTestAccount = confirm("No user logged in. Create a test teacher account for development?");
        
        if (createTestAccount) {
            // Create default test account
            localStorage.setItem('user', JSON.stringify({
                id: 'teacher1',
                username: 'teacher1',
                role: 'teacher'
            }));
            localStorage.setItem('authToken', 'test-token-for-development');
            localStorage.setItem('userInfo', JSON.stringify({
                username: 'teacher1',
                role: 'teacher',
                name: 'Test Teacher'
            }));
            
            return true;
        }
        
        return false;
    }
    
    // Otherwise, assume authenticated
    return true;
}

// Simple function to update user interface based on auth status
function updateUserInterface() {
    // Get user info from localStorage
    const userStr = localStorage.getItem('user');
    
    if (userStr) {
        try {
            const user = JSON.parse(userStr);
            
            // Update user name in navbar
            const userNameElement = document.getElementById('user-name');
            if (userNameElement) {
                userNameElement.textContent = user.username || 'User';
            }
            
            return user;
        } catch (e) {
            console.error('Error parsing user data:', e);
        }
    }
    
    return null;
}

// Simple function to log out
function logout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    window.location.href = 'login.html';
}