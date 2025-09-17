/*
COMP5241 Group 10 - API Client
Shared API utilities for all team members
*/

// API Client class
class APIClient {
    constructor(baseUrl = 'http://localhost:5000/api') {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem('authToken');
    }
    
    // Set authentication token
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('authToken', token);
        } else {
            localStorage.removeItem('authToken');
        }
    }
    
    // Get authentication headers
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        
        return headers;
    }
    
    // Generic request method
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: this.getHeaders(),
            ...options
        };
        
        try {
            showLoading(true);
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            showAlert(error.message, 'danger');
            throw error;
        } finally {
            showLoading(false);
        }
    }
    
    // GET request
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }
    
    // POST request
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }
    
    // PUT request
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }
    
    // DELETE request
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Create global API client instance
const api = new APIClient();

// Security API endpoints (Sunny's module)
const SecurityAPI = {
    // Authentication endpoints
    login: async (username, password) => {
        return api.post('/security/login', { username, password });
    },
    
    register: async (userData) => {
        return api.post('/security/register', userData);
    },
    
    logout: async () => {
        return api.post('/security/logout', {});
    },
    
    getProfile: async () => {
        return api.get('/security/profile');
    },
    
    // Health check
    healthCheck: async () => {
        return api.get('/security/health');
    }
};

// GenAI API endpoints (Ting's module)
const GenAIAPI = {
    // Content generation
    generateContent: async (prompt, options = {}) => {
        return api.post('/genai/generate', { prompt, ...options });
    },
    
    // Content analysis
    analyzeContent: async (content, analysisType) => {
        return api.post('/genai/analyze', { content, analysisType });
    },
    
    // Health check
    healthCheck: async () => {
        return api.get('/genai/health');
    }
};

// Courses API endpoints (Keith's module)
const CoursesAPI = {
    // Course management
    getCourses: async () => {
        return api.get('/courses/');
    },
    
    getCourse: async (courseId) => {
        return api.get(`/courses/${courseId}`);
    },
    
    createCourse: async (courseData) => {
        return api.post('/courses/', courseData);
    },
    
    updateCourse: async (courseId, courseData) => {
        return api.put(`/courses/${courseId}`, courseData);
    },
    
    // Enrollment
    enrollInCourse: async (courseId) => {
        return api.post(`/courses/${courseId}/enroll`, {});
    },
    
    getCourseStudents: async (courseId) => {
        return api.get(`/courses/${courseId}/students`);
    },
    
    // Health check
    healthCheck: async () => {
        return api.get('/courses/health');
    }
};

// Learning Activities API endpoints (Charlie's module)
const ActivitiesAPI = {
    // Activity management
    getActivities: async (courseId = null) => {
        const endpoint = courseId ? `/learning/activities?course_id=${courseId}` : '/learning/activities';
        return api.get(endpoint);
    },
    
    getActivity: async (activityId) => {
        return api.get(`/learning/activities/${activityId}`);
    },
    
    createActivity: async (activityData) => {
        return api.post('/learning/activities', activityData);
    },
    
    updateActivity: async (activityId, activityData) => {
        return api.put(`/learning/activities/${activityId}`, activityData);
    },
    
    // Submissions
    submitActivity: async (activityId, submissionData) => {
        return api.post(`/learning/activities/${activityId}/submit`, submissionData);
    },
    
    getSubmissions: async (activityId) => {
        return api.get(`/learning/activities/${activityId}/submissions`);
    },
    
    // Health check
    healthCheck: async () => {
        return api.get('/learning/health');
    }
};

// Admin API endpoints (Sunny's module)
const AdminAPI = {
    // User management
    getAllUsers: async () => {
        return api.get('/admin/users');
    },
    
    updateUser: async (userId, userData) => {
        return api.put(`/admin/users/${userId}`, userData);
    },
    
    activateUser: async (userId) => {
        return api.post(`/admin/users/${userId}/activate`, {});
    },
    
    // System management
    getSystemStats: async () => {
        return api.get('/admin/system/stats');
    },
    
    getAuditLogs: async () => {
        return api.get('/admin/audit-logs');
    },
    
    // Health check
    healthCheck: async () => {
        return api.get('/admin/health');
    }
};

// Health check for all modules
const HealthAPI = {
    checkAllModules: async () => {
        const results = {};
        
        try {
            results.main = await api.get('/health');
        } catch (error) {
            results.main = { status: 'error', message: error.message };
        }
        
        // Check each module
        const modules = {
            security: SecurityAPI.healthCheck,
            genai: GenAIAPI.healthCheck,
            courses: CoursesAPI.healthCheck,
            activities: ActivitiesAPI.healthCheck,
            admin: AdminAPI.healthCheck
        };
        
        for (const [module, healthCheck] of Object.entries(modules)) {
            try {
                results[module] = await healthCheck();
            } catch (error) {
                results[module] = { status: 'error', message: error.message };
            }
        }
        
        return results;
    }
};

// Export APIs for global use
window.api = api;
window.SecurityAPI = SecurityAPI;
window.GenAIAPI = GenAIAPI;
window.CoursesAPI = CoursesAPI;
window.ActivitiesAPI = ActivitiesAPI;
window.AdminAPI = AdminAPI;
window.HealthAPI = HealthAPI;

// Auto-test API connection on page load
document.addEventListener('DOMContentLoaded', async function() {
    try {
        console.log('Testing API connection...');
        const health = await api.get('/health');
        console.log('API connection successful:', health);
    } catch (error) {
        console.warn('API connection failed:', error.message);
        showAlert('Backend API is not available. Please ensure the Flask server is running.', 'warning');
    }
});
