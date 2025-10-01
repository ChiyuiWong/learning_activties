/*
COMP5241 Group 10 - Login Page JavaScript
Interactive login functionality with Bootstrap integration
*/

// Initialize login functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeLogin();
});

// Main initialization function
function initializeLogin() {
    initializeIllustrations();
    initializeFormHandlers();
    initializeDemoUsers();
    initializePasswordToggle();
    initializeRoleToggle();
    checkExistingLogin();
}

// Illustration management
const illustrations = [
    {
        content: `
            <div class="d-flex flex-column gap-3">
                <div class="d-flex align-items-center gap-3">
                    <div class="bg-success rounded d-flex align-items-center justify-content-center" style="width: 1.5rem; height: 1.5rem;">
                        <i class="bi bi-check text-white small"></i>
                    </div>
                    <div class="bg-light rounded flex-grow-1" style="height: 0.5rem;"></div>
                </div>
                <div class="d-flex align-items-center gap-3">
                    <div class="bg-success rounded d-flex align-items-center justify-content-center" style="width: 1.5rem; height: 1.5rem;">
                        <i class="bi bi-check text-white small"></i>
                    </div>
                    <div class="bg-light rounded flex-grow-1" style="height: 0.5rem;"></div>
                </div>
                <div class="d-flex align-items-center gap-3">
                    <div class="bg-light border rounded" style="width: 1.5rem; height: 1.5rem;"></div>
                    <div class="bg-light rounded flex-grow-1" style="height: 0.5rem;"></div>
                </div>
            </div>
        `,
        avatar: `
            <div class="bg-coral rounded-circle d-flex align-items-center justify-content-center" style="width: 4rem; height: 4rem;">
                <div class="bg-white rounded-circle" style="width: 2rem; height: 2rem;"></div>
            </div>
        `
    },
    {
        content: `
            <div class="d-flex flex-column gap-3">
                <div class="bg-primary bg-opacity-25 rounded-3 p-3">
                    <div class="bg-primary rounded mb-2" style="height: 0.5rem; width: 75%;"></div>
                    <div class="bg-primary bg-opacity-50 rounded" style="height: 0.25rem; width: 50%;"></div>
                </div>
                <div class="bg-success bg-opacity-25 rounded-3 p-3">
                    <div class="bg-success rounded mb-2" style="height: 0.5rem; width: 65%;"></div>
                    <div class="bg-success bg-opacity-50 rounded" style="height: 0.25rem; width: 75%;"></div>
                </div>
                <div class="bg-info bg-opacity-25 rounded-3 p-3">
                    <div class="bg-info rounded mb-2" style="height: 0.5rem; width: 50%;"></div>
                    <div class="bg-info bg-opacity-50 rounded" style="height: 0.25rem; width: 65%;"></div>
                </div>
            </div>
        `,
        avatar: `
            <div class="bg-primary rounded-circle d-flex align-items-center justify-content-center" style="width: 4rem; height: 4rem;">
                <div class="bg-white rounded border border-primary border-2" style="width: 2rem; height: 2rem;"></div>
            </div>
        `
    },
    {
        content: `
            <div class="row g-3">
                <div class="col-6">
                    <div class="bg-warning bg-opacity-25 rounded-3 p-3 d-flex align-items-center justify-content-center" style="aspect-ratio: 1;">
                        <div class="bg-warning rounded" style="width: 1.5rem; height: 1.5rem;"></div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="bg-danger bg-opacity-25 rounded-3 p-3 d-flex align-items-center justify-content-center" style="aspect-ratio: 1;">
                        <div class="bg-danger rounded-circle" style="width: 1.5rem; height: 1.5rem;"></div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="bg-info bg-opacity-25 rounded-3 p-3 d-flex align-items-center justify-content-center" style="aspect-ratio: 1;">
                        <div class="bg-info" style="width: 1.5rem; height: 1.5rem; clip-path: polygon(50% 0%, 0% 100%, 100% 100%);"></div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="bg-success bg-opacity-25 rounded-3 p-3 d-flex align-items-center justify-content-center" style="aspect-ratio: 1;">
                        <div class="bg-success rounded-2" style="width: 1.5rem; height: 1.5rem;"></div>
                    </div>
                </div>
            </div>
        `,
        avatar: `
            <div class="bg-info rounded-circle d-flex align-items-center justify-content-center" style="width: 4rem; height: 4rem;">
                <div class="bg-white rounded-2" style="width: 2rem; height: 2rem;"></div>
            </div>
        `
    }
];

let currentIllustration = 0;
let illustrationInterval;

function initializeIllustrations() {
    const illustrationContainer = document.getElementById('illustrationContainer');
    if (!illustrationContainer) return;

    // Set initial illustration
    changeIllustration(0);

    // Set up progress dots click handlers
    const progressDots = document.querySelectorAll('.progress-dot');
    progressDots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            changeIllustration(index);
            resetIllustrationTimer();
        });
    });

    // Auto-change illustrations
    startIllustrationTimer();
}

function changeIllustration(index) {
    const content = document.getElementById('illustrationContent');
    const avatarContainer = document.getElementById('avatarContainer');
    const progressDots = document.querySelectorAll('.progress-dot');

    if (!content || !avatarContainer || index >= illustrations.length) return;

    // Update progress dots
    progressDots.forEach((dot, i) => {
        dot.classList.toggle('active', i === index);
    });

    // Update content with fade effect
    content.style.opacity = '0';
    avatarContainer.style.opacity = '0';

    setTimeout(() => {
        content.innerHTML = illustrations[index].content;
        avatarContainer.innerHTML = illustrations[index].avatar;
        content.style.opacity = '1';
        avatarContainer.style.opacity = '1';
    }, 150);

    currentIllustration = index;
}

function startIllustrationTimer() {
    illustrationInterval = setInterval(() => {
        const nextIndex = (currentIllustration + 1) % illustrations.length;
        changeIllustration(nextIndex);
    }, 5000);
}

function resetIllustrationTimer() {
    clearInterval(illustrationInterval);
    startIllustrationTimer();
}

// Form handling
function initializeFormHandlers() {
    const loginForm = document.getElementById('loginForm');
    if (!loginForm) return;

    loginForm.addEventListener('submit', handleLogin);
}

async function handleLogin(event) {
    event.preventDefault();
    
    const submitButton = event.target.querySelector('button[type="submit"]');
    const signinText = submitButton.querySelector('.signin-text');
    const spinner = submitButton.querySelector('.spinner-border');
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;

    if (!username || !password) {
        showAlert('Please enter both username and password', 'warning');
        return;
    }

    // Show loading state
    submitButton.disabled = true;
    signinText.textContent = 'Signing In...';
    spinner.classList.remove('d-none');

    try {
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // For demo purposes, accept any credentials
        const userData = {
            username: username,
            role: username.includes('prof') || username.includes('dr') ? 'teacher' : 'student',
            name: getDisplayName(username)
        };

        // Store user info
        localStorage.setItem('userInfo', JSON.stringify(userData));
        
        // Show success modal
        showSuccessModal();
        
        // Redirect after modal is shown
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);

    } catch (error) {
        console.error('Login error:', error);
        showAlert('Login failed. Please try again.', 'danger');
    } finally {
        // Reset button state
        submitButton.disabled = false;
        signinText.textContent = 'Sign In';
        spinner.classList.add('d-none');
    }
}

function getDisplayName(username) {
    const displayNames = {
        'prof.smith': 'Prof. Smith',
        'dr.johnson': 'Dr. Johnson',
        'alice.wang': 'Alice Wang',
        'bob.chen': 'Bob Chen',
        'charlie.li': 'Charlie Li'
    };
    return displayNames[username] || username;
}

// Demo users functionality
function initializeDemoUsers() {
    const demoUserCards = document.querySelectorAll('.demo-user-card');
    
    demoUserCards.forEach(card => {
        card.addEventListener('click', () => {
            const username = card.dataset.username;
            const password = card.dataset.password;
            
            if (username && password) {
                quickLogin(username, password);
            }
        });
    });
}

function quickLogin(username, password) {
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginForm = document.getElementById('loginForm');
    
    if (!usernameInput || !passwordInput || !loginForm) return;
    
    usernameInput.value = username;
    passwordInput.value = password;
    
    // Trigger form submission after a short delay
    setTimeout(() => {
        loginForm.dispatchEvent(new Event('submit'));
    }, 300);
}

// Password toggle functionality
function initializePasswordToggle() {
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordInput = document.getElementById('password');
    const passwordIcon = document.getElementById('passwordIcon');
    
    if (!passwordToggle || !passwordInput || !passwordIcon) return;
    
    passwordToggle.addEventListener('click', () => {
        const isPassword = passwordInput.type === 'password';
        
        passwordInput.type = isPassword ? 'text' : 'password';
        passwordIcon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
    });
}

// Role toggle functionality
function initializeRoleToggle() {
    const teachersTab = document.getElementById('teachersTab');
    const studentsTab = document.getElementById('studentsTab');
    const teachersSection = document.getElementById('teachersSection');
    const studentsSection = document.getElementById('studentsSection');
    
    if (!teachersTab || !studentsTab || !teachersSection || !studentsSection) return;
    
    teachersTab.addEventListener('change', () => {
        if (teachersTab.checked) {
            teachersSection.classList.remove('d-none');
            studentsSection.classList.add('d-none');
        }
    });
    
    studentsTab.addEventListener('change', () => {
        if (studentsTab.checked) {
            studentsSection.classList.remove('d-none');
            teachersSection.classList.add('d-none');
        }
    });
}

// Success modal
function showSuccessModal() {
    const successModal = new bootstrap.Modal(document.getElementById('successModal'));
    successModal.show();
}

// Alert system
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alert-container');
    if (!alertContainer) return;
    
    const alertId = 'alert-' + Date.now();
    const alertClass = `alert-${type}`;
    
    const alertHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show shadow-sm" role="alert" id="${alertId}">
            <i class="bi bi-${getAlertIcon(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    alertContainer.insertAdjacentHTML('beforeend', alertHTML);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alertElement);
            bsAlert.close();
        }
    }, 5000);
}

function getAlertIcon(type) {
    const icons = {
        'success': 'check-circle-fill',
        'danger': 'exclamation-triangle-fill',
        'warning': 'exclamation-triangle-fill',
        'info': 'info-circle-fill'
    };
    return icons[type] || 'info-circle-fill';
}

// Check for existing login
function checkExistingLogin() {
    const userInfo = localStorage.getItem('userInfo');
    if (userInfo) {
        try {
            const userData = JSON.parse(userInfo);
            showAlert(`Welcome back, ${userData.name || userData.username}! Redirecting...`, 'info');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } catch (error) {
            localStorage.removeItem('userInfo');
        }
    }
}

// Handle browser back button and cleanup
window.addEventListener('beforeunload', () => {
    clearInterval(illustrationInterval);
});

// Export functions for global access (if needed)
window.LoginModule = {
    quickLogin,
    showAlert,
    showSuccessModal
};