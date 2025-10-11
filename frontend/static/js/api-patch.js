/* 
API Endpoint Fixes for Learning Activities
This script patches the API endpoints to fix URL mismatches 
*/

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('API endpoint patch loaded');
    
    // Add /api prefix to endpoints if needed
    const originalRequest = APIClient.prototype.request;
    
    APIClient.prototype.request = async function(endpoint, options = {}, is_include_header = false) {
        // Make sure all learning activity endpoints have the /api prefix
        if (endpoint.startsWith('/learning/') && !endpoint.startsWith('/api/learning/')) {
            endpoint = '/api' + endpoint;
            console.log('API endpoint patched to:', endpoint);
        }
        
        // Fix for health check endpoint
        if (endpoint === '/health') {
            endpoint = '/api/health';
            console.log('API endpoint patched to:', endpoint);
        }
        
        // Fix for security endpoints
        if (endpoint.startsWith('/security/') && !endpoint.startsWith('/api/security/')) {
            endpoint = '/api' + endpoint;
            console.log('API endpoint patched to:', endpoint);
        }
        
        // Fix the quiz typo (quizs -> quizzes)
        if (endpoint.includes('/learning/quizs/') || endpoint.includes('/api/learning/quizs/')) {
            endpoint = endpoint.replace('quizs', 'quizzes');
            console.log('Quiz endpoint fixed:', endpoint);
        }
        
        return originalRequest.call(this, endpoint, options, is_include_header);
    };
    
    console.log('API endpoints patched successfully');
});