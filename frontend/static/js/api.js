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
            console.log(`Making API request to: ${url}`);
            const response = await fetch(url, config);
            
            // Try to parse JSON response, but handle non-JSON responses gracefully
            let data;
            try {
                data = await response.json();
            } catch (parseError) {
                console.error('Failed to parse JSON response:', parseError);
                data = { error: 'Invalid response format' };
            }
            
            if (!response.ok) {
                console.error('API request failed:', data);
                throw new Error(data.message || 'API request failed');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            
            // Network-level errors (like connection refused, timeout, etc.)
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                console.error('Network connection issue - server might be down or unreachable');
                showAlert('Failed to connect to the server. Please check if the backend is running.', 'danger');
            } else {
                // Other API errors
                showAlert(error.message || 'An unknown error occurred', 'danger');
            }
            
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
const LearningActivitiesAPI = {
    // Quiz endpoints
    getQuizzes: async (courseId) => {
        const endpoint = courseId ? `/learning/quizzes/?course_id=${courseId}` : '/learning/quizzes/';
        return api.get(endpoint);
    },
    
    getQuiz: async (quizId) => {
        return api.get(`/learning/quizzes/${quizId}`);
    },
    
    createQuiz: async (quizData) => {
        return api.post('/learning/quizzes/', quizData);
    },
    
    startQuizAttempt: async (quizId) => {
        return api.post(`/learning/quizzes/${quizId}/attempt`);
    },
    
    submitQuiz: async (quizId, answers) => {
        return api.post(`/learning/quizzes/${quizId}/submit`, answers);
    },
    
    // Word Cloud endpoints
    getWordClouds: async (courseId) => {
        const endpoint = courseId ? `/learning/wordclouds/?course_id=${courseId}` : '/learning/wordclouds/';
        return api.get(endpoint);
    },
    
    getWordCloud: async (wordcloudId) => {
        return api.get(`/learning/wordclouds/${wordcloudId}`);
    },
    
    createWordCloud: async (wordcloudData) => {
        return api.post('/learning/wordclouds/', wordcloudData);
    },
    
    submitWord: async (wordcloudId, wordData) => {
        return api.post(`/learning/wordclouds/${wordcloudId}/submit`, wordData);
    },
    
    getWordCloudResults: async (wordcloudId) => {
        return api.get(`/learning/wordclouds/${wordcloudId}/results`);
    },
    
    // Short Answer endpoints
    getShortAnswers: async (courseId) => {
        const endpoint = courseId ? `/learning/shortanswers/?course_id=${courseId}` : '/learning/shortanswers/';
        return api.get(endpoint);
    },
    
    getShortAnswer: async (questionId) => {
        return api.get(`/learning/shortanswers/${questionId}`);
    },
    
    createShortAnswer: async (questionData) => {
        return api.post('/learning/shortanswers/', questionData);
    },
    
    submitAnswer: async (questionId, answerData) => {
        return api.post(`/learning/shortanswers/${questionId}/submit`, answerData);
    },
    
    provideFeedback: async (questionId, studentId, feedbackData) => {
        return api.post(`/learning/shortanswers/${questionId}/feedback/${studentId}`, feedbackData);
    },
    
    // Mini Game endpoints
    getMiniGames: async (courseId) => {
        const endpoint = courseId ? `/learning/minigames/?course_id=${courseId}` : '/learning/minigames/';
        return api.get(endpoint);
    },
    
    getMiniGame: async (gameId) => {
        return api.get(`/learning/minigames/${gameId}`);
    },
    
    createMiniGame: async (gameData) => {
        return api.post('/learning/minigames/', gameData);
    },
    
    submitGameScore: async (gameId, scoreData) => {
        return api.post(`/learning/minigames/${gameId}/score`, scoreData);
    },
    
    getGameLeaderboard: async (gameId) => {
        return api.get(`/learning/minigames/${gameId}/leaderboard`);
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

// Utility functions for API interactions
// Show or hide loading indicator
function showLoading(isLoading) {
    const loadingElement = document.getElementById('apiLoadingIndicator');
    if (!loadingElement) {
        // Create loading indicator if it doesn't exist
        const newLoader = document.createElement('div');
        newLoader.id = 'apiLoadingIndicator';
        newLoader.className = 'position-fixed top-0 end-0 p-3';
        newLoader.innerHTML = `
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        `;
        newLoader.style.display = isLoading ? 'block' : 'none';
        document.body.appendChild(newLoader);
    } else {
        loadingElement.style.display = isLoading ? 'block' : 'none';
    }
}

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    if (!alertContainer) {
        console.error('Alert container not found!');
        console.log('Alert:', message, 'Type:', type);
        return;
    }
    
    const alertId = 'alert-' + Date.now();
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.innerHTML += alertHTML;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert ? bsAlert.close() : alertElement.remove();
        }
    }, 5000);
}

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
