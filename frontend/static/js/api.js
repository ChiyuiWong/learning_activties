/*
COMP5241 Group 10 - API Client
Shared API utilities for all team members
*/

// API Client class
class APIClient {
    constructor(baseUrl = null) {
        // Auto-detect base URL to match current origin and avoid CORS issues
        if (!baseUrl) {
            baseUrl = `${window.location.protocol}//${window.location.host}`;
        }
        
        // Remove trailing slash if present
        let normalizedBase = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;

        // If base URL ends with /api, drop it because endpoints already add /api when needed
        if (normalizedBase.endsWith('/api')) {
            normalizedBase = normalizedBase.slice(0, -4);
        }

        this.baseUrl = normalizedBase;
        this.token = localStorage.getItem('authToken');
        
        // For test pages - create a default user if none exists
        if (!localStorage.getItem('user') && !localStorage.getItem('authToken')) {
            // Create a test user for demo purposes
            localStorage.setItem('user', JSON.stringify({
                id: 'test123',
                username: 'testuser',
                email: 'test@example.com',
                role: 'teacher'
            }));
            localStorage.setItem('authToken', 'test-token-for-development');
            console.log('Created demo user for testing');
        }
    }
    
    getCookie(name) {
      const value = `; ${document.cookie}`;
      const parts = value.split(`; ${name}=`);
      if (parts.length === 2) return parts.pop().split(';').shift();
    }
    
    // Get authentication headers
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        // Add JWT token if it exists
        const token = localStorage.getItem('access_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
            console.log('Adding JWT token to request headers');
        } else {
            console.log('No JWT token found in localStorage');
        }
        
        // Add CSRF token if it exists
        const csrfToken = this.getCookie('csrf_access_token');
        if (csrfToken) {
            headers['X-CSRF-TOKEN'] = csrfToken;
        }
        
        return headers;
    }
    
    // Set the auth token
    setToken(token) {
        this.token = token;
        if (token) {
            localStorage.setItem('authToken', token);
            console.log('Token saved to localStorage');
        } else {
            localStorage.removeItem('authToken');
            console.log('Token removed from localStorage');
        }
    }
    
    // Normalize API endpoint paths
    normalizeEndpoint(endpoint) {
        // Start with a clean endpoint
        let normalized = endpoint;

        // Remove any double /api prefixes
        while (normalized.includes('/api/api/')) {
            normalized = normalized.replace('/api/api/', '/api/');
        }

        // Add /api prefix if needed
        if (!normalized.startsWith('/api/')) {
            if (normalized.startsWith('/learning/') || 
                normalized.startsWith('/security/') || 
                normalized === '/health') {
                normalized = '/api' + normalized;
            }
        }

        // Fix quiz typo
        if (normalized.includes('/quizs/')) {
            normalized = normalized.replace('/quizs/', '/quizzes/');
        }

        // Log if we made changes
        if (normalized !== endpoint) {
            console.log('Endpoint normalized:', {
                from: endpoint,
                to: normalized
            });
        }

        return normalized;
    }

    // Generic request method
    async request(endpoint, options = {}, is_include_header = false) {
        // Normalize the endpoint
        const normalizedEndpoint = this.normalizeEndpoint(endpoint);
        
        const url = `${this.baseUrl}${normalizedEndpoint}`;
        const config = {
            headers: this.getHeaders(),
            credentials: 'include',  // Important: Include cookies with requests
            mode: 'cors',
            ...options
        };
        
        try {
            showLoading(true);
            console.log(`Making API request to: ${url}`);
            console.log('Request headers:', config.headers);
            const response = await fetch(url, config);
            
            // Try to parse JSON response, but handle non-JSON responses gracefully
            let data;

            try {
                if(response.headers.get('Content-Type') === 'application/json') {
                    data = await response.json();
                } else {
                    data = await response.blob();
                }
            } catch (parseError) {
                data = { error: 'Invalid response format' };
            }
            
            if (!response.ok) {
                console.error('API request failed:', data);
                const error = new Error(data.message || 'API request failed');
                error.status = response.status;
                error.statusText = response.statusText;
                error.data = data;
                
                // Handle specific status codes - log to console only, no user notifications
                switch (response.status) {
                    case 400:
                        console.warn('Bad Request:', data.message || 'Invalid request');
                        break;
                    case 401:
                        // Expected when not logged in - just log silently
                        console.debug('Authentication required for:', endpoint);
                        break;
                    case 403:
                        console.warn('Access forbidden for:', endpoint);
                        break;
                    case 404:
                        console.warn('Resource not found:', endpoint);
                        break;
                    case 500:
                        console.error('Server error for:', endpoint, data.message);
                        break;
                    default:
                        console.warn('Request failed:', response.status, endpoint, data.message || 'Unknown error');
                        break;
                }
                
                // Don't show any popup notifications for API errors
                
                throw error;
            }
            if(is_include_header) {
                return [data, response.headers];
            }
            return data;
        } catch (error) {
            console.error('API Error:', error);
            
            // Network-level errors (like connection refused, timeout, etc.)
            if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
                console.error('Network connection issue - server might be down or unreachable');
                // Don't show popup for network errors - just log to console
            } else {
                // Other API errors - log to console only
                console.error('API error:', error.message || 'An unknown error occurred');
            }
            
            throw error;
        } finally {
            showLoading(false);
        }
    }
    
    // GET request
    async get(endpoint, options = {}) {
        try {
            return await this.request(endpoint, { method: 'GET', ...options });
        } catch (error) {
            // For learning activity endpoints, gracefully handle failures
            if (endpoint.startsWith('/learning/') || endpoint.startsWith('/api/learning/')) {
                console.warn(`Learning activity endpoint ${endpoint} failed:`, error);
                
                // For list endpoints (ending with / or ?), return empty array
                if (endpoint.includes('?') || endpoint.endsWith('/')) {
                    return [];
                }
                
                // For individual activity endpoints, return a default object based on type
                if (endpoint.includes('/quizzes/')) {
                    return {
                        id: endpoint.split('/').pop(),
                        title: 'Sample Quiz (Offline)',
                        description: 'This quiz is not available right now',
                        questions: [],
                        course_id: 'COMP5241',
                        is_active: false
                    };
                } else if (endpoint.includes('/polls/')) {
                    return {
                        id: endpoint.split('/').pop(),
                        question: 'Sample Poll (Offline)',
                        options: [],
                        course_id: 'COMP5241',
                        is_active: false
                    };
                } else if (endpoint.includes('/wordclouds/')) {
                    return {
                        id: endpoint.split('/').pop(),
                        title: 'Sample Word Cloud (Offline)',
                        description: 'This word cloud is not available right now',
                        course_id: 'COMP5241',
                        is_active: false
                    };
                } else if (endpoint.includes('/shortanswers/')) {
                    return {
                        id: endpoint.split('/').pop(),
                        question: 'Sample Short Answer (Offline)',
                        description: 'This question is not available right now',
                        course_id: 'COMP5241',
                        is_active: false
                    };
                }
                
                // Default fallback
                return [];
            }
            throw error;
        }
    }

    
    // POST request
    async post(endpoint, data, is_include_header = false) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        }, is_include_header);
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
    
    updateQuiz: async (quizId, quizData) => {
        return api.put(`/learning/quizzes/${quizId}`, quizData);
    },
    
    getQuizResults: async (quizId) => {
        return api.get(`/learning/quizzes/${quizId}/results`);
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
    ,
    // Poll endpoints
    getPolls: async (courseId) => {
        const endpoint = courseId ? `/learning/polls/?course_id=${courseId}` : '/learning/polls/';
        return api.get(endpoint);
    },
    getPoll: async (pollId) => {
        return api.get(`/learning/polls/${pollId}`);
    },
    createPoll: async (pollData) => {
        return api.post('/learning/polls', pollData);
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
            activities: LearningActivitiesAPI.healthCheck,
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
window.ActivitiesAPI = LearningActivitiesAPI;
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
        // Don't show popup for connection test failures - just log to console
    }
});
