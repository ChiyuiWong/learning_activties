/*
COMP5241 Group 10 - Learning Activities Frontend
Complete integration with backend APIs
*/

// Global notification function that delegates to the instance if available
function showNotification(message, type = 'info') {
    // If we have a global instance of LearningActivitiesManager, use it
    if (window.learningActivities) {
        window.learningActivities.showNotification(message, type);
    } else {
        // Fallback for when the instance isn't available
        console.log(`Notification (${type}): ${message}`);
        
        // Create a simple notification element
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `alert alert-${type} notification-toast`;
        notificationDiv.innerHTML = message;
        
        // Add to document
        document.body.appendChild(notificationDiv);
        
        // Add visible class for animation
        setTimeout(() => notificationDiv.classList.add('visible'), 10);
        
        // Remove after delay
        setTimeout(() => {
            notificationDiv.classList.remove('visible');
            setTimeout(() => notificationDiv.remove(), 500);
        }, 3000);
    }
}

// Learning Activities Manager
class LearningActivitiesManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.currentView = 'overview';
        this.currentActivity = null;
        this.userRole = 'student'; // Will be set from user data
        this.stats = {
            total: 0,
            active: 0,
            responses: 0,
            pending: 0,
            byType: {}
        };
        
        // Call initialization functions
        this.init();
        this.setupRefreshInterval();
    }
    
    setUserRole(role) {
        this.userRole = role;
        console.log(`User role set to ${role} in Learning Activities Manager`);
        // Refresh the UI based on the new role
        this.refreshCurrentView();
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notificationDiv = document.createElement('div');
        notificationDiv.className = `alert alert-${type} notification-toast`;
        notificationDiv.innerHTML = message;
        
        // Add to document
        document.body.appendChild(notificationDiv);
        
        // Add visible class for animation
        setTimeout(() => notificationDiv.classList.add('visible'), 10);
        
        // Remove after delay
        setTimeout(() => {
            notificationDiv.classList.remove('visible');
            setTimeout(() => notificationDiv.remove(), 500);
        }, 3000);
    }

    setupRefreshInterval() {
        // Refresh stats every 30 seconds
        setInterval(() => this.loadActivityCounts(), 30000);
    }

    // Basic poll view (show poll question and options, allow teacher to view results)
    showPollInterface(poll) {
        const content = this.getActivityContainer();
        let html = `
            <div class="mb-3">
                <button class="btn btn-outline-secondary" onclick="learningActivities.showMyActivities()">
                    ← 返回活动列表
                </button>
            </div>
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">📊 ${poll.question}</h5>
                </div>
                <div class="card-body">
                    <p class="mb-3">选择一个选项进行投票：</p>
                    <div class="mb-3">
                        ${poll.options.map((opt, idx) => `
                            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border rounded">
                                <span>${opt.text}</span>
                                <div>
                                    <span class="badge bg-secondary me-2">${opt.votes||0} 票</span>
                                    <button class="btn btn-sm btn-primary" onclick="learningActivities.vote('${poll.id}', ${idx})">
                                        投票
                                    </button>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-outline-primary" onclick="learningActivities.refreshPoll('${poll.id}')">刷新结果</button>
                    </div>
                </div>
            </div>
        `;
        content.innerHTML = html;
    }
    
    async vote(pollId, optionIndex) {
        try {
            console.log(`Voting on poll ${pollId}, option ${optionIndex}`);
            
            const response = await this.api.post(`/learning/polls/${pollId}/vote`, {
                option_index: optionIndex
            });
            
            this.showNotification('投票成功！', 'success');
            
            // Refresh the poll to show updated results
            this.refreshPoll(pollId);
            
        } catch (error) {
            console.error('Error voting:', error);
            // Only show notification for non-auth errors
            if (error.status !== 401) {
                this.showNotification('投票失败，请稍后重试', 'error');
            }
        }
    }
    
    async refreshPoll(pollId) {
        try {
            const poll = await this.api.get(`/learning/polls/${pollId}`);
            this.showPollInterface(poll);
        } catch (error) {
            console.error('Error refreshing poll:', error);
            // Don't show notification for refresh errors - they're not critical
        }
    }

    // Show create form for different activity types
    showCreateForm(type) {
        // Redirect to the appropriate creation page based on activity type
        if (type === 'quiz') {
            window.location.href = 'test_quiz.html';
            return;
        }
        else if (type === 'wordcloud') {
            window.location.href = 'test_wordcloud.html';
            return;
        }
        else if (type === 'shortanswer') {
            window.location.href = 'test_shortanswer.html';
            return;
        }
        else if (type === 'poll') {
            window.location.href = 'test_poll.html';
            return;
        }
        
        const content = document.getElementById('activity-details-content');
        const typeInfo = this.getActivityTypeInfo(type);
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5>${typeInfo.icon} Create New ${typeInfo.name}</h5>
                </div>
                <div class="card-body">
                    <form id="create-activity-form" class="needs-validation" novalidate>
                        <!-- Basic Info -->
                        <div class="mb-4">
                            <h6 class="border-bottom pb-2">Basic Information</h6>
                            <div class="mb-3">
                                <label class="form-label">Title*</label>
                                <input type="text" class="form-control" name="title" required>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Description</label>
                                <textarea class="form-control" name="description" rows="3"></textarea>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Instructions</label>
                                <textarea class="form-control" name="instructions" rows="3"></textarea>
                            </div>
                        </div>

                        <!-- Schedule -->
                        <div class="mb-4">
                            <h6 class="border-bottom pb-2">Schedule</h6>
                            <div class="row">
                                <div class="col-md-4">
                                    <label class="form-label">Start Date</label>
                                    <input type="datetime-local" class="form-control" name="start_date">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Due Date</label>
                                    <input type="datetime-local" class="form-control" name="due_date">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">End Date</label>
                                    <input type="datetime-local" class="form-control" name="end_date">
                                </div>
                            </div>
                        </div>

                        <!-- Settings -->
                        <div class="mb-4">
                            <h6 class="border-bottom pb-2">Settings</h6>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Max Score</label>
                                        <input type="number" class="form-control" name="max_score" value="100">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Time Limit (minutes)</label>
                                        <input type="number" class="form-control" name="time_limit">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Max Attempts (0 = unlimited)</label>
                                        <input type="number" class="form-control" name="max_attempts" value="0">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Passing Score</label>
                                        <input type="number" class="form-control" name="passing_score">
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Type-specific content -->
                        <div class="mb-4" id="type-specific-content">
                            ${this.getTypeSpecificFields(type)}
                        </div>

                        <!-- Advanced Settings -->
                        <div class="mb-4">
                            <h6 class="border-bottom pb-2">Advanced Settings</h6>
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Status</label>
                                        <select class="form-select" name="status">
                                            <option value="draft">Draft</option>
                                            <option value="published">Published</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label class="form-label">Visibility</label>
                                        <select class="form-select" name="visibility">
                                            <option value="public">Public</option>
                                            <option value="private">Private</option>
                                            <option value="group">Group</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            <div class="mb-3">
                                <label class="form-label">Tags (comma-separated)</label>
                                <input type="text" class="form-control" name="tags" 
                                       placeholder="e.g., homework, quiz, chapter1">
                            </div>
                        </div>

                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary">Create Activity</button>
                            <button type="button" class="btn btn-outline-secondary" 
                                    onclick="learningActivities.switchView('overview')">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;

        // Handle form submission
        document.getElementById('create-activity-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleActivitySubmit(e.target, type);
        });

        // Add any type-specific event handlers
        this.addTypeSpecificHandlers(type);
    }
    
    init() {
        console.log('Initializing Learning Activities Manager...');
        this.bindEventListeners();
        this.loadActivityCounts();
    }

    getTypeSpecificFields(type) {
        switch(type) {
            case 'quiz':
                return `
                    <h6 class="border-bottom pb-2">Quiz Settings</h6>
                    
                    <div class="row mb-4">
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Time Limit (minutes)</label>
                                <input type="number" class="form-control" name="time_limit" min="0" value="30">
                                <small class="form-text text-muted">Leave blank for no time limit</small>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-3">
                                <label class="form-label">Passing Score (%)</label>
                                <input type="number" class="form-control" name="passing_score" min="0" max="100" value="60">
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="shuffle_questions" name="shuffle_questions">
                            <label class="form-check-label" for="shuffle_questions">Shuffle Questions</label>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <div class="form-check form-switch">
                            <input class="form-check-input" type="checkbox" id="show_results" name="show_results" checked>
                            <label class="form-check-label" for="show_results">Show Results After Completion</label>
                        </div>
                    </div>
                    
                    <h6 class="border-bottom pb-2 mt-4">Quiz Questions</h6>
                    <div id="quiz-questions" class="mb-4">
                        <div class="quiz-question card mb-3">
                            <div class="card-header d-flex justify-content-between align-items-center bg-light">
                                <h6 class="mb-0">Question 1</h6>
                                <div>
                                    <span class="badge bg-primary me-2" title="Question Points">1 pt</span>
                                </div>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <label class="form-label">Question Text*</label>
                                    <input type="text" class="form-control" name="questions[0].text" required 
                                           placeholder="Enter your question here...">
                                </div>
                                
                                <div class="mb-3">
                                    <label class="form-label">Question Type</label>
                                    <select class="form-select question-type-select" name="questions[0].type">
                                        <option value="multiple_choice">Multiple Choice</option>
                                        <option value="true_false">True/False</option>
                                    </select>
                                </div>
                                
                                <div class="options-container">
                                    <p class="fw-medium mb-2">Options <small class="text-muted">(select the correct answer)</small></p>
                                    <div class="option-group mb-2">
                                        <div class="input-group">
                                            <div class="input-group-text">
                                                <input type="radio" name="questions[0].correct" value="0">
                                            </div>
                                            <input type="text" class="form-control" name="questions[0].options[0]" 
                                                   placeholder="Option 1" required>
                                        </div>
                                    </div>
                                    <div class="option-group mb-2">
                                        <div class="input-group">
                                            <div class="input-group-text">
                                                <input type="radio" name="questions[0].correct" value="1">
                                            </div>
                                            <input type="text" class="form-control" name="questions[0].options[1]" 
                                                   placeholder="Option 2" required>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mt-3 mb-2">
                                    <button type="button" class="btn btn-sm btn-outline-secondary" 
                                            onclick="learningActivities.addQuizOption(this)">
                                        <i class="bi bi-plus-circle"></i> Add Option
                                    </button>
                                </div>
                                
                                <div class="mb-3 mt-4">
                                    <label class="form-label">Explanation (Optional)</label>
                                    <textarea class="form-control" name="questions[0].explanation" 
                                              placeholder="Explanation to show after answering..."></textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <button type="button" class="btn btn-outline-primary mb-4" 
                            onclick="learningActivities.addQuizQuestion()">
                        <i class="bi bi-plus-circle"></i> Add Question
                    </button>
                `;

            case 'wordcloud':
                return `
                    <h6 class="border-bottom pb-2">Word Cloud Settings</h6>
                    <div class="mb-3">
                        <label class="form-label">Prompt*</label>
                        <textarea class="form-control" name="prompt" required
                                  placeholder="Enter the prompt for students..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Max Submissions per User</label>
                        <input type="number" class="form-control" name="max_submissions_per_user" 
                               value="3" min="1" max="10">
                    </div>
                `;

            case 'shortanswer':
                return `
                    <h6 class="border-bottom pb-2">Short Answer Settings</h6>
                    <div class="mb-3">
                        <label class="form-label">Question*</label>
                        <textarea class="form-control" name="question" required></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Answer Guidelines</label>
                        <textarea class="form-control" name="answer_guidelines"
                                  placeholder="Provide guidelines for students..."></textarea>
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Max Length (characters)</label>
                        <input type="number" class="form-control" name="max_length" value="1000">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Rubric</label>
                        <textarea class="form-control" name="rubric"
                                  placeholder="Describe how answers will be graded..."></textarea>
                    </div>
                `;

            default:
                return `<div class="alert alert-info">No additional settings required for this type.</div>`;
        }
    }

    addTypeSpecificHandlers(type) {
        if (type === 'quiz') {
            // Initialize question counter
            this.questionCounter = 1;
            
            // Add event listeners for question type changes
            document.querySelectorAll('.question-type-select').forEach(select => {
                select.addEventListener('change', (e) => {
                    this.handleQuestionTypeChange(e.target);
                });
            });
            
            // Initialize Bootstrap tooltips if available
            if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
                tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl);
                });
            }
            
            // Add validation for form before submission
            const form = document.getElementById('create-activity-form');
            form.addEventListener('submit', (e) => {
                // We're handling this in the main submit handler
                // Just making sure we have questions
                const questions = document.querySelectorAll('.quiz-question');
                if (questions.length === 0) {
                    e.preventDefault();
                    this.showNotification('Please add at least one question to your quiz.', 'warning');
                    return false;
                }
            });
        }
    }

    addQuizQuestion() {
        const container = document.getElementById('quiz-questions');
        const questionNum = this.questionCounter + 1;
        
        const questionHtml = `
            <div class="quiz-question card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center bg-light">
                    <h6 class="mb-0">Question ${questionNum}</h6>
                    <div>
                        <span class="badge bg-primary me-2" title="Question Points">1 pt</span>
                        <button type="button" class="btn btn-sm btn-outline-danger" title="Remove Question"
                                onclick="this.closest('.quiz-question').remove()">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <label class="form-label">Question Text*</label>
                        <input type="text" class="form-control" name="questions[${this.questionCounter}].text" required
                               placeholder="Enter your question here...">
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Question Type</label>
                        <select class="form-select question-type-select" name="questions[${this.questionCounter}].type" 
                                onchange="learningActivities.handleQuestionTypeChange(this)">
                            <option value="multiple_choice">Multiple Choice</option>
                            <option value="true_false">True/False</option>
                        </select>
                    </div>
                    
                    <div class="options-container">
                        <p class="fw-medium mb-2">Options <small class="text-muted">(select the correct answer)</small></p>
                        <div class="option-group mb-2">
                            <div class="input-group">
                                <div class="input-group-text">
                                    <input type="radio" name="questions[${this.questionCounter}].correct" value="0">
                                </div>
                                <input type="text" class="form-control" name="questions[${this.questionCounter}].options[0]" 
                                       placeholder="Option 1" required>
                            </div>
                        </div>
                        <div class="option-group mb-2">
                            <div class="input-group">
                                <div class="input-group-text">
                                    <input type="radio" name="questions[${this.questionCounter}].correct" value="1">
                                </div>
                                <input type="text" class="form-control" name="questions[${this.questionCounter}].options[1]" 
                                       placeholder="Option 2" required>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-3 mb-2">
                        <button type="button" class="btn btn-sm btn-outline-secondary" 
                                onclick="learningActivities.addQuizOption(this)">
                            <i class="bi bi-plus-circle"></i> Add Option
                        </button>
                    </div>
                    
                    <div class="mb-3 mt-4">
                        <label class="form-label">Explanation (Optional)</label>
                        <textarea class="form-control" name="questions[${this.questionCounter}].explanation" 
                                  placeholder="Explanation to show after answering..."></textarea>
                    </div>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', questionHtml);
        this.questionCounter++;
    }

    addQuizOption(button) {
        const optionsContainer = button.closest('.card-body').querySelector('.options-container');
        const questionDiv = button.closest('.quiz-question');
        const questionIndex = Array.from(questionDiv.parentNode.children).indexOf(questionDiv);
        const optionCount = optionsContainer.querySelectorAll('.option-group').length;
        
        const optionHtml = `
            <div class="option-group mb-2">
                <div class="input-group">
                    <div class="input-group-text">
                        <input type="radio" name="questions[${questionIndex}].correct" value="${optionCount}">
                    </div>
                    <input type="text" class="form-control" name="questions[${questionIndex}].options[${optionCount}]" 
                           placeholder="Option ${optionCount + 1}" required>
                    <button type="button" class="btn btn-outline-danger" 
                            onclick="this.closest('.option-group').remove()">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
        
        optionsContainer.insertAdjacentHTML('beforeend', optionHtml);
    }
    
    handleQuestionTypeChange(selectElement) {
        const questionDiv = selectElement.closest('.quiz-question');
        const optionsContainer = questionDiv.querySelector('.options-container');
        const questionType = selectElement.value;
        
        if (questionType === 'true_false') {
            // For True/False questions, we provide fixed options
            optionsContainer.innerHTML = `
                <p class="fw-medium mb-2">Options <small class="text-muted">(select the correct answer)</small></p>
                <div class="option-group mb-2">
                    <div class="input-group">
                        <div class="input-group-text">
                            <input type="radio" name="questions[${Array.from(questionDiv.parentNode.children).indexOf(questionDiv)}].correct" value="0" checked>
                        </div>
                        <input type="text" class="form-control" name="questions[${Array.from(questionDiv.parentNode.children).indexOf(questionDiv)}].options[0]" 
                               value="True" readonly>
                    </div>
                </div>
                <div class="option-group mb-2">
                    <div class="input-group">
                        <div class="input-group-text">
                            <input type="radio" name="questions[${Array.from(questionDiv.parentNode.children).indexOf(questionDiv)}].correct" value="1">
                        </div>
                        <input type="text" class="form-control" name="questions[${Array.from(questionDiv.parentNode.children).indexOf(questionDiv)}].options[1]" 
                               value="False" readonly>
                    </div>
                </div>
            `;
            
            // Hide the add option button for True/False questions
            const addOptionBtn = questionDiv.querySelector('button[onclick*="addQuizOption"]');
            if (addOptionBtn) {
                addOptionBtn.style.display = 'none';
            }
        } else {
            // For multiple choice, reset to default state if needed
            const addOptionBtn = questionDiv.querySelector('button[onclick*="addQuizOption"]');
            if (addOptionBtn) {
                addOptionBtn.style.display = '';
            }
            
            // Only reset if it was previously a true/false question
            const options = optionsContainer.querySelectorAll('.option-group');
            if (options.length === 2) {
                const option1 = options[0].querySelector('input[type="text"]');
                const option2 = options[1].querySelector('input[type="text"]');
                
                if (option1.value === 'True' && option2.value === 'False') {
                    // Reset to empty options
                    option1.value = '';
                    option1.readOnly = false;
                    option2.value = '';
                    option2.readOnly = false;
                }
            }
        }
    }

    async handleActivitySubmit(form, type) {
        try {
            const formData = new FormData(form);
            const data = {
                title: formData.get('title'),
                description: formData.get('description'),
                activity_type: type,
                course_id: 'COMP5241', // TODO: Get from current course context
                instructions: formData.get('instructions'),
                max_score: parseInt(formData.get('max_score')) || 100,
                // Convert time limit from seconds to minutes for backend
                time_limit: this.convertSecondsToMinutes(formData.get('time_limit')),
                start_date: formData.get('start_date') || null,
                due_date: formData.get('due_date') || null,
                end_date: formData.get('end_date') || null,
                status: formData.get('status'),
                visibility: formData.get('visibility'),
                tags: formData.get('tags')?.split(',').map(tag => tag.trim()) || [],
                metadata: {}
            };

            // Add type-specific data
            switch(type) {
                case 'quiz':
                    // Process quiz questions
                    data.metadata.questions = this.processQuizQuestions(form);
                    
                    // If no questions added, alert and stop
                    if (data.metadata.questions.length === 0) {
                        this.showNotification('Please add at least one question to your quiz.', 'warning');
                        return;
                    }
                    
                    // Check if at least one option is marked correct in each question
                    const missingCorrect = data.metadata.questions.some(q => 
                        !q.options.some(opt => opt.is_correct === true));
                    
                    if (missingCorrect) {
                        this.showNotification('Please select a correct answer for each question.', 'warning');
                        return;
                    }
                    
                    // Add quiz settings to metadata
                    data.metadata.shuffle_questions = form.querySelector('#shuffle_questions')?.checked || false;
                    data.metadata.show_results = form.querySelector('#show_results')?.checked || false;
                    data.metadata.passing_score = parseInt(formData.get('passing_score') || 60);
                    
                    // Calculate total points
                    data.metadata.total_points = data.metadata.questions.reduce((sum, q) => sum + (q.points || 1), 0);
                    
                    // Set the attempt_limit to unlimited
                    data.metadata.attempt_limit = 0; // 0 means unlimited attempts
                    break;
                    
                case 'poll':
                    const pollOptions = [];
                    const optionsContainer = form.querySelector('#poll-options');
                    if (optionsContainer) {
                        const optionInputs = optionsContainer.querySelectorAll('input[name="options[]"]');
                        optionInputs.forEach(input => {
                            if (input.value.trim()) {
                                pollOptions.push(input.value.trim());
                            }
                        });
                    }
                    data.metadata.question = formData.get('poll-question');
                    data.metadata.options = pollOptions;
                    data.metadata.is_anonymous = formData.get('poll-anonymous') === 'on';
                    break;
                    
                case 'wordcloud':
                    data.metadata.prompt = formData.get('prompt');
                    data.metadata.max_submissions_per_user = parseInt(formData.get('max_submissions_per_user'));
                    data.metadata.min_word_length = parseInt(formData.get('wordcloud-min-length')) || 3;
                    data.metadata.filter_profanity = formData.get('wordcloud-filter-profanity') === 'on';
                    break;
                    
                case 'shortanswer':
                    data.metadata.question = formData.get('question');
                    data.metadata.answer_guidelines = formData.get('answer_guidelines');
                    data.metadata.max_length = parseInt(formData.get('max_length'));
                    data.metadata.rubric = formData.get('rubric');
                    break;
            }

            console.log('Creating activity:', type, data);
            
            // Add a note about time limit conversion
            console.log('Note: Time limit has been converted from seconds to minutes for backend compatibility');
            
            // Use the unified activity creation endpoint
            const response = await this.api.post('/learning/activities/', data);
            console.log('Creation response:', response);

            if (response && response.success) {
                this.showNotification(`${type.charAt(0).toUpperCase() + type.slice(1)} created successfully!`, 'success');
                
                // If we have an activity ID, navigate to it
                if (response.activity && response.activity.id) {
                    setTimeout(() => {
                        this.switchView('overview');
                        this.showActivityList(type);
                    }, 1000);
                } else {
                    // Otherwise go back to the overview
                    this.switchView('overview');
                    this.refreshCurrentView();
                }
            } else {
                throw new Error(response.error || 'Failed to create activity');
            }

        } catch (error) {
            console.error('Error creating activity:', error);
            this.showNotification(error.message || 'Failed to create activity', 'error');
        }
    }

    processQuizQuestions(form) {
        const questions = [];
        const questionDivs = form.querySelectorAll('.quiz-question');
        
        questionDivs.forEach((div, index) => {
            // Find the actual index in the form's naming scheme (in case questions were deleted)
            const namePrefix = div.querySelector('input[name$=".text"]').name.split('.')[0];
            const questionIndex = namePrefix.replace('questions[', '').replace(']', '');
            
            const options = [];
            const optionInputs = div.querySelectorAll(`input[name^="${namePrefix}.options"]`);
            const correctOption = div.querySelector(`input[name="${namePrefix}.correct"]:checked`)?.value;
            
            if (!correctOption && optionInputs.length > 0) {
                console.warn(`No correct option selected for question ${parseInt(questionIndex) + 1}. Defaulting to first option.`);
            }
            
            optionInputs.forEach((input, optIndex) => {
                options.push({
                    text: input.value,
                    is_correct: optIndex.toString() === correctOption,
                    explanation: '' // This is now in the question-level explanation field
                });
            });
            
            // Get question type from select
            const questionTypeSelect = div.querySelector(`select[name="${namePrefix}.type"]`);
            const questionType = questionTypeSelect ? questionTypeSelect.value : 'multiple_choice';
            
            // Get explanation if it exists
            const explanationField = div.querySelector(`textarea[name="${namePrefix}.explanation"]`);
            const explanation = explanationField ? explanationField.value : '';
            
            questions.push({
                text: div.querySelector(`input[name="${namePrefix}.text"]`).value,
                options: options,
                points: 1, // Currently fixed at 1 point per question
                question_type: questionType,
                explanation: explanation
            });
        });
        
        return questions;
    }
    
    bindEventListeners() {
        // Activity view switcher buttons
        document.querySelectorAll('[data-activity-view]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.getAttribute('data-activity-view');
                this.switchView(view);
            });
        });
        
        // Activity type buttons (quiz, wordcloud, etc.)
        document.querySelectorAll('[data-activity-type]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const type = e.target.getAttribute('data-activity-type');
                this.showActivityList(type);
            });
        });
        
        // Create activity type cards
        document.querySelectorAll('[data-create-type]').forEach(card => {
            card.addEventListener('click', (e) => {
                console.log('Card clicked:', e.target, e.currentTarget);
                const cardElement = e.target.closest('[data-create-type]');
                console.log('Card element:', cardElement);
                if (cardElement) {
                    const type = cardElement.getAttribute('data-create-type');
                    console.log('Activity type:', type);
                    this.showCreateForm(type);
                } else {
                    console.error('Could not find parent with data-create-type attribute');
                }
            });
        });
        
        // Back to activities button
        const backBtn = document.getElementById('back-to-activities');
        if (backBtn) {
            backBtn.addEventListener('click', () => {
                this.switchView('overview');
            });
        }
        
        // Refresh button
        const refreshBtn = document.getElementById('refresh-activity');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.refreshCurrentView();
            });
        }
    }
    
    switchView(view) {
        console.log(`Switching to view: ${view}`);
        this.currentView = view;
        
        // Hide all views
        document.querySelectorAll('.activity-view').forEach(v => v.classList.add('d-none'));
        
        // Update button states
        document.querySelectorAll('[data-activity-view]').forEach(btn => {
            btn.classList.toggle('active', btn.getAttribute('data-activity-view') === view);
        });
        
        // Show selected view
        switch(view) {
            case 'overview':
                document.getElementById('activities-overview').classList.remove('d-none');
                this.loadActivityCounts();
                break;
            case 'my-activities':
                document.getElementById('my-activities').classList.remove('d-none');
                this.loadMyActivities();
                break;
            case 'create':
                document.getElementById('create-activity').classList.remove('d-none');
                break;
        }
    }
    
    refreshCurrentView() {
        // Refresh the current view based on what view is active
        console.log(`Refreshing current view: ${this.currentView}`);
        
        switch(this.currentView) {
            case 'overview':
                this.loadActivityCounts();
                break;
            case 'my-activities':
                this.loadMyActivities();
                break;
            case 'detail':
                if (this.currentActivity) {
                    const activityType = this.currentActivity.activity_type || this.currentActivity.type;
                    this.openActivity(activityType, this.currentActivity.id);
                }
                break;
        }
        
        // Show a notification
        this.showNotification('View refreshed', 'info');
    }
    
    async loadActivityCounts() {
        try {
            console.log('Loading activity counts...');
            // Load counts for each activity type
            const courseId = 'COMP5241'; // TODO: Get from current course context
            
            // Using the improved API client that handles errors gracefully
            const quizzes = await this.api.get(`/learning/quizzes/?course_id=${courseId}`);
            const wordclouds = await this.api.get(`/learning/wordclouds/?course_id=${courseId}`);
            const shortanswers = await this.api.get(`/learning/shortanswers/?course_id=${courseId}`);
            const polls = await this.api.get(`/learning/polls/?course_id=${courseId}`);
            
            console.log('Activity counts loaded:', { 
                quizzes: quizzes.length,
                wordclouds: wordclouds.length,
                shortanswers: shortanswers.length,
                polls: polls.length
            });
            
            const updateCount = (id, items, suffix) => {
                const el = document.getElementById(id);
                if (el) {
                    if (Array.isArray(items)) {
                        el.textContent = `${items.length} ${suffix}`;
                    } else {
                        el.textContent = `0 ${suffix}`;
                        console.warn(`Invalid data for ${id}:`, items);
                    }
                }
            };
            
            updateCount('quiz-count', quizzes, 'available');
            updateCount('wordcloud-count', wordclouds, 'active');
            updateCount('poll-count', polls, 'active');
            updateCount('shortanswer-count', shortanswers, 'questions');
            
        } catch (error) {
            console.error('Error loading activity counts:', error);
            // Set error states
            ['quiz-count', 'wordcloud-count', 'shortanswer-count'].forEach(id => {
                document.getElementById(id).textContent = 'Error loading';
            });
        }
    }

    // Include polls in the counts
    async loadPollCount() {
        try {
            const courseId = 'COMP5241';
            const polls = await this.api.get(`/learning/polls/?course_id=${courseId}`);
            const el = document.getElementById('poll-count');
            if (el) el.textContent = `${polls.length} active`;
        } catch (e) {
            const el = document.getElementById('poll-count');
            if (el) el.textContent = 'Error loading';
        }
    }
    
    async loadMyActivities() {
        const content = document.getElementById('my-activities-content');
        content.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading your activities...</p>
            </div>
        `;
        
        try {
            const courseId = 'COMP5241'; // TODO: Get from current course context
            console.log('Loading activities for course:', courseId);
            
            // First try to load from MongoDB polls collection directly
            let polls = [];
            try {
                polls = await this.api.get(`/learning/polls/?course_id=${courseId}`);
                console.log('Polls loaded:', polls);
            } catch (err) {
                console.warn('Error fetching polls:', err);
                polls = [];
            }
            
            // Load all other activity types
            let [quizzes, wordclouds, shortanswers] = [[], [], []];
            
            try {
                [quizzes, wordclouds, shortanswers] = await Promise.all([
                    this.api.get(`/learning/quizzes/?course_id=${courseId}`),
                    this.api.get(`/learning/wordclouds/?course_id=${courseId}`),
                    this.api.get(`/learning/shortanswers/?course_id=${courseId}`)
                ]);
                console.log('Other activities loaded:', { quizzes, wordclouds, shortanswers });
            } catch (err) {
                console.warn('Error fetching some activities:', err);
            }
            
            const activities = [
                ...quizzes.map(q => ({...q, type: 'quiz', icon: '📝', color: 'primary'})),
                ...wordclouds.map(w => ({...w, type: 'wordcloud', icon: '☁️', color: 'success'})),
                ...shortanswers.map(s => ({...s, type: 'shortanswer', icon: '📄', color: 'info'})),
                ...polls.map(p => ({...p, type: 'poll', icon: '📊', color: 'secondary'}))
            ];
            
            if (activities.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-5">
                        <h5>No activities available</h5>
                        <p class="text-muted">Check back later for new learning activities!</p>
                    </div>
                `;
                return;
            }
            
            // Group activities by type
            // Debug what we have
            console.log('Combined activities for display:', activities);
            
            // If no activities at all, show message
            if (activities.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-5">
                        <div class="mb-4">
                            <i class="bi bi-clipboard-x text-muted" style="font-size: 3rem;"></i>
                        </div>
                        <h5>No activities found</h5>
                        <p class="text-muted">You haven't created any learning activities yet.</p>
                        <button class="btn btn-primary mt-3" data-activity-view="create">
                            <i class="bi bi-plus-circle me-1"></i> Create New Activity
                        </button>
                    </div>
                `;
                
                // Bind event handler to the create button
                const createBtn = content.querySelector('[data-activity-view="create"]');
                if (createBtn) {
                    createBtn.addEventListener('click', () => this.showActivityView('create'));
                }
                
                return;
            }
            
            const groupedActivities = activities.reduce((groups, activity) => {
                const type = activity.type;
                if (!groups[type]) groups[type] = [];
                groups[type].push(activity);
                return groups;
            }, {});
            
            let html = '';
            for (const [type, items] of Object.entries(groupedActivities)) {
                const typeInfo = this.getActivityTypeInfo(type);
                html += `
                    <div class="mb-4">
                        <h6 class="border-bottom pb-2">${typeInfo.icon} ${typeInfo.name}</h6>
                        <div class="row g-3">
                `;
                
                items.forEach(activity => {
                    html += `
                        <div class="col-md-6 col-lg-4">
                            <div class="card h-100 border-${activity.color}">
                                <div class="card-body">
                                    <h6 class="card-title">${activity.title || activity.question}</h6>
                                    <p class="card-text text-muted small">${activity.description || activity.prompt || 'No description'}</p>
                                    <div class="d-flex justify-content-between align-items-center">
                                        <small class="text-muted">
                                            ${activity.expires_at ? `Expires: ${new Date(activity.expires_at).toLocaleDateString()}` : 'No deadline'}
                                        </small>
                                        <button class="btn btn-sm btn-${activity.color}" 
                                                onclick="learningActivities.openActivity('${activity.type}', '${activity.id || activity._id}')">
                                            Open
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            content.innerHTML = html;
            
        } catch (error) {
            console.error('Error loading my activities:', error);
            
            // Show different messages based on error type
            if (error.status === 401) {
                content.innerHTML = `
                    <div class="alert alert-info text-center">
                        <h5><i class="bi bi-lock"></i> 需要登录</h5>
                        <p>请先登录以查看您的学习活动</p>
                        <a href="/login.html" class="btn btn-primary">
                            <i class="bi bi-person-circle"></i> 立即登录
                        </a>
                    </div>
                `;
            } else {
                content.innerHTML = `
                    <div class="alert alert-warning text-center">
                        <h6>暂时无法加载活动</h6>
                        <p>请稍后再试</p>
                        <button class="btn btn-outline-primary btn-sm" onclick="learningActivities.loadMyActivities()">
                            重新加载
                        </button>
                    </div>
                `;
            }
        }
    }
    
    getActivityTypeInfo(type) {
        const typeMap = {
            quiz: { name: 'Quizzes', icon: '📝' },
            wordcloud: { name: 'Word Clouds', icon: '☁️' },
            shortanswer: { name: 'Short Answers', icon: '📄' },
            poll: { name: 'Polls', icon: '📊' }
        };
        return typeMap[type] || { name: 'Unknown', icon: '❓' };
    }
    
    async showActivityList(type) {
        console.log(`Showing activity list for type: ${type}`);
        
        // Switch to activity details view
        document.querySelectorAll('.activity-view').forEach(v => v.classList.add('d-none'));
        document.getElementById('activity-details').classList.remove('d-none');
        
        const content = document.getElementById('activity-details-content');
        content.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading ${type} activities...</p>
            </div>
        `;
        
        try {
            const courseId = 'COMP5241'; // TODO: Get from current course context
            const activities = await this.api.get(`/learning/${type}s/?course_id=${courseId}`);
            
            const typeInfo = this.getActivityTypeInfo(type);
            
            let html = `
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <h4>${typeInfo.icon} ${typeInfo.name}</h4>
                    ${this.userRole === 'teacher' ? `<button class="btn btn-primary" onclick="learningActivities.showCreateForm('${type}')">Create New</button>` : ''}
                </div>
            `;
            
            if (activities.length === 0) {
                html += `
                    <div class="text-center py-5">
                        <h5>No ${type} activities available</h5>
                        <p class="text-muted">Check back later or create a new activity!</p>
                    </div>
                `;
            } else {
                html += '<div class="row g-3">';
                activities.forEach(activity => {
                    html += this.renderActivityCard(activity, type);
                });
                html += '</div>';
            }
            
            content.innerHTML = html;
            
        } catch (error) {
            console.error(`Error loading ${type} activities:`, error);
            content.innerHTML = `
                <div class="alert alert-danger">
                    <h6>Error Loading Activities</h6>
                    <p>Unable to load ${type} activities. Please try again.</p>
                </div>
            `;
        }
    }
    
    renderActivityCard(activity, type) {
        const colorMap = {
            quiz: 'primary',
            wordcloud: 'success', 
            shortanswer: 'info',
            poll: 'secondary'
        };
        const color = colorMap[type] || 'secondary';
        
        // Check if user is the creator (for delete button)
        const isCreator = activity.created_by === this.api.userId || activity.created_by === window.currentUser?.id;
        
        return `
            <div class="col-md-6 col-lg-4">
                <div class="card h-100 border-${color}">
                    <div class="card-body">
                        <h6 class="card-title">${activity.title || activity.question}</h6>
                        <p class="card-text text-muted small">${activity.description || activity.prompt || 'No description'}</p>
                        ${this.renderActivityStats(activity, type)}
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <small class="text-muted">
                                ${activity.expires_at ? `Expires: ${new Date(activity.expires_at).toLocaleDateString()}` : 'No deadline'}
                            </small>
                            <div class="btn-group" role="group">
                                <button class="btn btn-${color}" onclick="learningActivities.openActivity('${type}', '${activity.id || activity._id}')">
                                    ${type === 'quiz' ? 'Take Quiz' : type === 'wordcloud' ? 'Submit Words' : type === 'shortanswer' ? 'Answer' : type === 'poll' ? 'View Poll' : 'View Activity'}
                                </button>
                                ${isCreator ? `<button class="btn btn-outline-danger btn-sm" onclick="learningActivities.deleteActivity('${type}', '${activity.id || activity._id}')" title="Delete Activity">
                                    <i class="bi bi-trash"></i>
                                </button>` : ''}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderActivityStats(activity, type) {
        // Add type-specific statistics
        switch(type) {
            case 'quiz':
                const questionCount = activity.questions ? activity.questions.length : 0;
                const timeLimit = activity.time_limit ? `${activity.time_limit}m` : 'No limit';
                return `<small class="text-muted d-block">Questions: ${questionCount} • Time: ${timeLimit}</small>`;
            
            case 'wordcloud':
                const maxSubmissions = activity.max_submissions_per_user || 3;
                const submissionCount = activity.submissions ? activity.submissions.length : 0;
                return `<small class="text-muted d-block">Max submissions: ${maxSubmissions} • Total words: ${submissionCount}</small>`;
            
            case 'shortanswer':
                const maxLength = activity.max_length || 1000;
                const submissionCount2 = activity.submissions ? activity.submissions.length : 0;
                return `<small class="text-muted d-block">Max length: ${maxLength} chars • Submissions: ${submissionCount2}</small>`;
            
            default:
                return '';
        }
    }
    
    async openActivity(type, activityId) {
        console.log(`Opening ${type} activity: ${activityId}`);
        
        try {
            // Map activity types to correct API endpoints
            let endpoint;
            switch(type) {
                case 'quiz':
                    endpoint = `/learning/quizzes/${activityId}`;
                    break;
                case 'poll':
                    endpoint = `/learning/polls/${activityId}`;
                    break;
                case 'wordcloud':
                    endpoint = `/learning/wordclouds/${activityId}`;
                    break;
                case 'shortanswer':
                    endpoint = `/learning/shortanswers/${activityId}`;
                    break;
                default:
                    throw new Error(`Unknown activity type: ${type}`);
            }
            
            // Load activity details
            const activity = await this.api.get(endpoint);
            this.currentActivity = { type, activity, id: activityId };
            
            // Check if we're in "my-activities" context
            const myActivitiesContent = document.getElementById('my-activities-content');
            const isInMyActivities = myActivitiesContent && !myActivitiesContent.closest('.d-none');
            
            if (isInMyActivities) {
                // We're in "my-activities" page, so we need to ensure the interface shows in the right place
                console.log('Opening activity in my-activities context');
            }
            
            // Show activity interface based on type
            switch(type) {
                case 'quiz':
                    this.showQuizInterface(activity);
                    break;
                case 'poll':
                    this.showPollInterface(activity);
                    break;
                case 'wordcloud':
                    this.showWordCloudInterface(activity);
                    break;
                case 'shortanswer':
                    this.showShortAnswerInterface(activity);
                    break;
            }
            
        } catch (error) {
            console.error(`Error opening ${type} activity:`, error);
            // Only show error notification for non-authentication errors
            if (error.status !== 401) {
                this.showNotification(`无法打开活动，请稍后重试`, 'error');
            }
        }
    }
    
    getActivityContainer() {
        // Try to find the appropriate container for displaying activity content
        let container = document.getElementById('activity-details-content');
        
        // If activity-details-content doesn't exist or is not visible, use my-activities-content
        if (!container || container.closest('.d-none')) {
            container = document.getElementById('my-activities-content');
        }
        
        if (!container) {
            // Fallback: create a temporary container
            container = document.createElement('div');
            container.className = 'container mt-4';
            document.body.appendChild(container);
        }
        return container;
    }
    
    showMyActivities() {
        // Reload the activities list
        this.loadMyActivities();
    }
    
    showQuizInterface(quiz) {
        const content = this.getActivityContainer();
        
        let html = `
            <div class="mb-3">
                <button class="btn btn-outline-secondary" onclick="learningActivities.showMyActivities()">
                    ← 返回活动列表
                </button>
            </div>
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">📝 ${quiz.title}</h5>
                    <p class="mb-0 text-muted">${quiz.description}</p>
                </div>
                <div class="card-body">
                    <div class="mb-3">
                        <strong>Instructions:</strong>
                        <ul class="mt-2">
                            <li>Answer all questions to complete the quiz</li>
                            ${quiz.time_limit ? `<li>You have ${quiz.time_limit} minutes to complete</li>` : ''}
                            <li>Click "Submit Quiz" when you're done</li>
                        </ul>
                    </div>
                    
                    <button class="btn btn-primary btn-lg" onclick="learningActivities.startQuiz('${quiz.id || quiz._id}')">
                        Start Quiz
                    </button>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
    }
    
    async startQuiz(quizId) {
        try {
            console.log('Starting quiz:', quizId);
            
            // Load quiz questions directly
            const quiz = await this.api.get(`/learning/quizzes/${quizId}`);
            console.log('Quiz loaded:', quiz);
            
            // Generate a simple attempt ID for tracking
            const attemptId = 'attempt_' + Date.now();
            
            this.showQuizQuestions(quiz, attemptId);
            
        } catch (error) {
            console.error('Error starting quiz:', error);
            this.showNotification('Error starting quiz: ' + error.message, 'error');
        }
    }
    
    showQuizQuestions(quiz, attemptId) {
        const content = this.getActivityContainer();
        
        let html = `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">📝 ${quiz.title}</h5>
                    ${quiz.time_limit ? `<div class="badge bg-warning" id="quiz-timer">Time: ${quiz.time_limit}:00</div>` : ''}
                </div>
                <div class="card-body">
                    <form id="quiz-form" data-attempt-id="${attemptId}">
        `;
        
        quiz.questions.forEach((question, index) => {
            html += `
                <div class="question-container mb-4 p-3 border rounded">
                    <h6>Question ${index + 1} <span class="badge bg-secondary">${question.points} pts</span></h6>
                    <p class="fw-bold">${question.text}</p>
                    
                    <div class="options">
            `;
            
            question.options.forEach((option, optionIndex) => {
                const inputType = question.question_type === 'multiple_select' ? 'checkbox' : 'radio';
                const inputName = `question_${index}`;
                
                html += `
                    <div class="form-check">
                        <input class="form-check-input" type="${inputType}" name="${inputName}" 
                               value="${optionIndex}" id="q${index}_opt${optionIndex}">
                        <label class="form-check-label" for="q${index}_opt${optionIndex}">
                            ${option.text}
                        </label>
                    </div>
                `;
            });
            
            html += `
                    </div>
                </div>
            `;
        });
        
        html += `
                    <div class="text-center">
                        <button type="submit" class="btn btn-success btn-lg">Submit Quiz</button>
                    </div>
                </form>
            </div>
        </div>
        `;
        
        content.innerHTML = html;
        
        // Bind quiz form submission
        document.getElementById('quiz-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitQuiz(quiz.id || quiz._id, attemptId);
        });
        
        // Start timer if time limit is set
        if (quiz.time_limit) {
            this.startQuizTimer(quiz.time_limit);
        }
    }
    
    startQuizTimer(timeLimit) {
        let timeLeft = timeLimit * 60; // Convert to seconds
        const timerElement = document.getElementById('quiz-timer');
        
        const timer = setInterval(() => {
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            timerElement.textContent = `Time: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            if (timeLeft <= 0) {
                clearInterval(timer);
                timerElement.textContent = 'Time Up!';
                timerElement.className = 'badge bg-danger';
                
                // Auto-submit quiz
                const form = document.getElementById('quiz-form');
                if (form) {
                    const submitEvent = new Event('submit');
                    form.dispatchEvent(submitEvent);
                }
            }
            
            timeLeft--;
        }, 1000);
    }
    
    async submitQuiz(quizId, attemptId) {
        try {
            console.log('Submitting quiz:', quizId);
            
            const form = document.getElementById('quiz-form');
            if (!form) {
                throw new Error('Quiz form not found');
            }
            
            // Prepare answers
            const answers = [];
            const questions = document.querySelectorAll('.question-container');
            
            console.log('Found questions:', questions.length);
            
            questions.forEach((questionEl, index) => {
                const selectedOptions = [];
                const inputs = questionEl.querySelectorAll('input:checked');
                
                inputs.forEach(input => {
                    selectedOptions.push(parseInt(input.value));
                });
                
                answers.push({
                    question_index: index,
                    selected_options: selectedOptions
                });
            });
            
            console.log('Prepared answers:', answers);
            
            // Submit quiz
            const result = await this.api.post(`/learning/quizzes/${quizId}/submit`, {
                answers: answers
            });
            
            console.log('Quiz submission result:', result);
            this.showQuizResults(result);
            
        } catch (error) {
            console.error('Error submitting quiz:', error);
            this.showNotification('提交测验失败: ' + error.message, 'error');
        }
    }
    
    showQuizResults(result) {
        const content = this.getActivityContainer();
        
        const percentage = result.score_percentage || 0;
        const scoreColor = percentage >= 80 ? 'success' : percentage >= 60 ? 'warning' : 'danger';
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">📝 Quiz Completed!</h5>
                </div>
                <div class="card-body text-center">
                    <div class="mb-4">
                        <h2 class="text-${scoreColor}">${percentage.toFixed(1)}%</h2>
                        <p class="lead">Score: ${result.points_earned || 0} / ${result.total_points || 0} points</p>
                    </div>
                    
                    ${result.feedback ? `
                        <div class="alert alert-info">
                            <h6>Feedback</h6>
                            <p>${result.feedback}</p>
                        </div>
                    ` : ''}
                    
                    <div class="mt-4">
                        <button class="btn btn-primary me-2" onclick="learningActivities.switchView('my-activities')">
                            View My Activities
                        </button>
                        <button class="btn btn-outline-primary" onclick="learningActivities.switchView('overview')">
                            Back to Overview
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    showWordCloudInterface(wordcloud) {
        const content = this.getActivityContainer();
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">☁️ ${wordcloud.title}</h5>
                    <p class="mb-0 text-muted">${wordcloud.prompt}</p>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Submit Words</h6>
                            <div class="mb-3">
                                <input type="text" class="form-control" id="word-input" 
                                       placeholder="Enter a word or phrase" maxlength="50">
                                <small class="text-muted">Maximum ${wordcloud.max_submissions_per_user || 3} submissions per user</small>
                            </div>
                            <button class="btn btn-success" onclick="learningActivities.submitWord('${wordcloud.id || wordcloud._id}')">
                                Submit Word
                            </button>
                            
                            <div id="user-submissions" class="mt-3">
                                <!-- User's submitted words will appear here -->
                            </div>
                        </div>
                        <div class="col-md-6">
                            <h6>Word Cloud</h6>
                            <div id="wordcloud-visualization" class="border rounded p-3" style="min-height: 300px;">
                                <!-- Word cloud visualization will appear here -->
                            </div>
                        </div>
                    </div>
                    <div class="card-footer">
                        <button class="btn btn-secondary" onclick="learningActivities.showMyActivities()">
                            返回活动列表
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Load current word cloud data
        this.loadWordCloudData(wordcloud.id || wordcloud._id);
        
        // Enable Enter key submission
        document.getElementById('word-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.submitWord(wordcloud.id || wordcloud._id);
            }
        });
    }
    
    async loadWordCloudData(wordcloudId) {
        try {
            const results = await this.api.get(`/learning/wordclouds/${wordcloudId}/results`);
            
            // Show word cloud visualization
            this.renderWordCloud(results.words);
            
            // Show user submissions (if any)
            // This would require knowing the current user ID
            
        } catch (error) {
            console.error('Error loading word cloud data:', error);
        }
    }
    
    renderWordCloud(words) {
        const container = document.getElementById('wordcloud-visualization');
        
        if (!words || words.length === 0) {
            container.innerHTML = '<p class="text-muted text-center">No words submitted yet. Be the first!</p>';
            return;
        }
        
        // Add anti-translation attributes to container
        container.setAttribute('translate', 'no');
        container.setAttribute('class', container.className + ' notranslate');
        
        // Detect language function
        const detectLanguage = (text) => {
            return /^[a-zA-Z\s\-'\.]+$/.test(text.trim()) ? 'english' : 'chinese';
        };
        
        // Create canvas for professional word cloud
        const canvas = document.createElement('canvas');
        canvas.width = 800;
        canvas.height = 500;
        canvas.style.cssText = `
            width: 100%;
            height: 500px;
            max-width: 800px;
            border: none;
            border-radius: 15px;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
            display: block;
            margin: 0 auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        `;
        canvas.setAttribute('translate', 'no');
        canvas.className = 'notranslate';
        
        const ctx = canvas.getContext('2d');
        
        // Clear canvas with gradient background
        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, '#f8f9fa');
        gradient.addColorStop(1, '#ffffff');
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Sort words by frequency (highest first)
        const sortedWords = words.sort((a, b) => {
            const freqA = a.frequency || a.value || a.weight || 1;
            const freqB = b.frequency || b.value || b.weight || 1;
            return freqB - freqA;
        });
        
        console.log('Rendering professional word cloud with words:', sortedWords.length, sortedWords);
        
        // Professional color palettes like the reference image
        const professionalColors = [
            '#8B5CF6', // Purple (like "Transform")
            '#3B82F6', // Blue (like "Data") 
            '#10B981', // Green (like "count")
            '#F59E0B', // Orange (like "generator")
            '#EF4444', // Red (like "font")
            '#EC4899', // Pink (like "Into Insights")
            '#6366F1', // Indigo (like "word")
            '#84CC16', // Lime (like "visualize")
            '#06B6D4', // Cyan (like "cloud")
            '#8B5A2B', // Brown (like "print")
            '#7C3AED', // Violet
            '#059669'  // Emerald
        ];
        
        // Advanced word cloud layout algorithm
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const placedWords = []; // Track placed words to avoid overlap
        
        sortedWords.forEach((wordData, index) => {
            const frequency = wordData.frequency || wordData.value || wordData.weight || 1;
            const text = wordData.text || wordData.word || String(wordData) || 'Unknown';
            const language = detectLanguage(text);
            
            console.log(`Word ${index}:`, { text, frequency, wordData });
            
            // Calculate font size based on frequency (like the reference image)
            let fontSize;
            if (index === 0) {
                fontSize = 72; // Largest word like "Data" and "Insights"
            } else if (index < 3) {
                fontSize = 56; // Second tier like "Transform", "Into"
            } else if (index < 6) {
                fontSize = 42; // Third tier
            } else if (index < 10) {
                fontSize = 32; // Fourth tier
            } else {
                fontSize = 24; // Smallest words
            }
            
            // Adjust font size based on actual frequency
            fontSize = Math.max(fontSize * (0.5 + frequency * 0.1), 20);
            fontSize = Math.min(fontSize, 80);
            
            // Color selection
            const color = professionalColors[index % professionalColors.length];
            
            // Find position using improved layout algorithm
            let x, y, attempts = 0;
            let positioned = false;
            
            while (!positioned && attempts < 150) {
                if (attempts === 0 && index === 0) {
                    // First word goes in center
                    x = centerX;
                    y = centerY;
                } else {
                    // Use golden angle spiral for natural distribution
                    const angle = attempts * 137.5 * Math.PI / 180; // Golden angle
                    const radius = Math.sqrt(attempts) * 25; // Spiral outward more gradually
                    x = centerX + Math.cos(angle) * radius;
                    y = centerY + Math.sin(angle) * radius;
                    
                    // Keep within canvas bounds with padding
                    const padding = fontSize / 2;
                    x = Math.max(padding, Math.min(canvas.width - padding, x));
                    y = Math.max(padding, Math.min(canvas.height - padding, y));
                }
                
                // Improved collision detection
                let collision = false;
                for (let placed of placedWords) {
                    const dx = x - placed.x;
                    const dy = y - placed.y;
                    const distance = Math.sqrt(dx * dx + dy * dy);
                    const minDistance = (fontSize + placed.fontSize) * 0.5; // Closer packing
                    
                    if (distance < minDistance) {
                        collision = true;
                        break;
                    }
                }
                
                if (!collision) {
                    positioned = true;
                    placedWords.push({ x, y, fontSize, text });
                }
                attempts++;
            }
            
            // If still not positioned after many attempts, place it anyway
            if (!positioned) {
                x = centerX + (Math.random() - 0.5) * canvas.width * 0.8;
                y = centerY + (Math.random() - 0.5) * canvas.height * 0.8;
                placedWords.push({ x, y, fontSize, text });
            }
            
            // No rotation - keep all words horizontal like in the reference image
            const rotation = 0;
            
            // Draw the word
            ctx.save();
            ctx.translate(x, y);
            ctx.rotate(rotation);
            
            // Font styling (Impact font like professional word clouds)
            ctx.font = `bold ${fontSize}px Impact, "Arial Black", sans-serif`;
            ctx.fillStyle = color;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            // Add subtle shadow for depth
            ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
            ctx.shadowBlur = 3;
            ctx.shadowOffsetX = 1;
            ctx.shadowOffsetY = 1;
            
            // Draw the word
            ctx.fillText(text, 0, 0);
            
            // Add subtle stroke for better visibility
            ctx.shadowColor = 'transparent';
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.7)';
            ctx.lineWidth = 1;
            ctx.strokeText(text, 0, 0);
            
            ctx.restore();
        });
        
        // Create container
        container.innerHTML = '';
        
        const mainContainer = document.createElement('div');
        mainContainer.className = 'word-cloud-container notranslate';
        mainContainer.setAttribute('translate', 'no');
        mainContainer.style.textAlign = 'center';
        
        const canvasContainer = document.createElement('div');
        canvasContainer.className = 'canvas-container';
        canvasContainer.style.marginBottom = '15px';
        canvasContainer.appendChild(canvas);
        
        // Statistics
        const englishWords = sortedWords.filter(w => detectLanguage(w.text || w.word || String(w)) === 'english');
        const chineseWords = sortedWords.filter(w => detectLanguage(w.text || w.word || String(w)) === 'chinese');
        
        const statsContainer = document.createElement('div');
        statsContainer.className = 'word-cloud-stats';
        statsContainer.innerHTML = `
            <small class="text-muted">
                <span class="badge bg-primary me-2">${englishWords.length} English</span>
                <span class="badge bg-success me-2">${chineseWords.length} Chinese</span>
                <span class="badge bg-secondary">${words.length} Total Words</span>
            </small>
        `;
        
        mainContainer.appendChild(canvasContainer);
        mainContainer.appendChild(statsContainer);
        container.appendChild(mainContainer);
        
        // Force disable translation
        setTimeout(() => {
            container.setAttribute('translate', 'no');
            container.querySelectorAll('*').forEach(element => {
                element.setAttribute('translate', 'no');
            });
        }, 100);
        
        console.log('Professional word cloud rendered successfully!');
    }
    
    async submitWord(wordcloudId) {
        const wordInput = document.getElementById('word-input');
        const word = wordInput.value.trim();
        
        if (!word) {
            this.showNotification('Please enter a word', 'warning');
            return;
        }
        
        try {
            const result = await this.api.post(`/learning/wordclouds/${wordcloudId}/submit`, {
                word: word
            });
            
            this.showNotification('Word submitted successfully!', 'success');
            wordInput.value = '';
            
            // Reload word cloud data
            this.loadWordCloudData(wordcloudId);
            
        } catch (error) {
            console.error('Error submitting word:', error);
            // Only show notification for non-auth errors
            if (error.status !== 401) {
                this.showNotification('提交失败，请稍后重试', 'error');
            }
        }
    }
    
    showShortAnswerInterface(question) {
        const content = this.getActivityContainer();
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">📄 Short Answer Question</h5>
                </div>
                <div class="card-body">
                    <h6>Question:</h6>
                    <p class="lead">${question.text || question.question}</p>
                    
                    ${question.answer_hint ? `
                        <div class="alert alert-info">
                            <strong>Hint:</strong> ${question.answer_hint}
                        </div>
                    ` : ''}
                    
                    <div class="mb-3">
                        <label for="answer-text" class="form-label">Your Answer:</label>
                        <textarea class="form-control" id="answer-text" rows="8" 
                                  maxlength="${question.max_length || 1000}"
                                  placeholder="Enter your answer here..."></textarea>
                        <small class="text-muted">Maximum ${question.max_length || 1000} characters</small>
                    </div>
                    
                    <button class="btn btn-info btn-lg" onclick="learningActivities.submitAnswer('${question.id || question._id}')">
                        Submit Answer
                    </button>
                </div>
            </div>
        `;
    }
    
    async submitAnswer(questionId) {
        const answerText = document.getElementById('answer-text').value.trim();
        
        if (!answerText) {
            this.showNotification('Please enter an answer', 'warning');
            return;
        }
        
        try {
            const result = await this.api.post(`/learning/shortanswers/${questionId}/submit`, {
                answer: answerText
            });
            
            this.showNotification('Answer submitted successfully!', 'success');
            
            // Show submission confirmation
            const content = document.getElementById('activity-details-content');
            content.innerHTML = `
                <div class="card">
                    <div class="card-header">
                        <h5 class="mb-0">📄 Answer Submitted</h5>
                    </div>
                    <div class="card-body text-center">
                        <div class="mb-4">
                            <i class="bi bi-check-circle text-success" style="font-size: 3rem;"></i>
                            <h4 class="mt-2">Answer Submitted Successfully!</h4>
                            <p class="text-muted">Your answer has been submitted and is waiting for teacher feedback.</p>
                        </div>
                        
                        <div class="mt-4">
                            <button class="btn btn-primary me-2" onclick="learningActivities.switchView('my-activities')">
                                View My Activities
                            </button>
                            <button class="btn btn-outline-primary" onclick="learningActivities.switchView('overview')">
                                Back to Overview
                            </button>
                        </div>
                    </div>
                </div>
            `;
            
        } catch (error) {
            console.error('Error submitting answer:', error);
            this.showNotification('Error submitting answer: ' + error.message, 'error');
        }
    }
    
    // Mini-game interface functionality removed
    
    // Game leaderboard functionality removed
    
    // Start mini-game functionality removed
    
    showCreateForm(type) {
        // If type is quiz, redirect to the quiz creation page
        if (type === 'quiz') {
            window.location.href = 'test_quiz.html';
            return;
        }
        
        console.log(`Showing create form for: ${type}`);
        // For other activity types that are still in development
        this.showNotification(`${type} creation form is being developed!`, 'info');
    }
    
    refreshCurrentView() {
        switch(this.currentView) {
            case 'overview':
                this.loadActivityCounts();
                break;
            case 'my-activities':
                this.loadMyActivities();
                break;
            default:
                break;
        }
    }
    
    setUserRole(role) {
        this.userRole = role;
        // Show/hide teacher-only features
        document.querySelectorAll('[data-role="teacher"]').forEach(el => {
            el.style.display = role === 'teacher' ? 'block' : 'none';
        });
    }
    
    /**
     * Helper function to convert time from seconds to minutes
     * Frontend stores time in seconds, but backend expects minutes
     * @param {string|number} timeInSeconds - Time value in seconds
     * @returns {number|null} - Time value in minutes, rounded up, or null if no time provided
     */
    convertSecondsToMinutes(timeInSeconds) {
        if (!timeInSeconds) return null;
        
        const seconds = parseInt(timeInSeconds);
        if (isNaN(seconds) || seconds <= 0) return null;
        
        // Convert to minutes and round up to ensure minimum time is met
        return Math.ceil(seconds / 60);
    }
    
    /**
     * Delete an activity
     * @param {string} type - Activity type (quiz, poll, shortanswer, wordcloud)
     * @param {string} activityId - ID of the activity to delete
     */
    async deleteActivity(type, activityId) {
        try {
            // Confirm deletion
            const confirmMessage = `Are you sure you want to delete this ${type}? This action cannot be undone.`;
            if (!confirm(confirmMessage)) {
                return;
            }
            
            // Show loading state
            this.showNotification('Deleting activity...', 'info');
            
            // Call the appropriate delete endpoint
            let endpoint;
            switch(type) {
                case 'quiz':
                    endpoint = `/learning/delete/quizzes/${activityId}`;
                    break;
                case 'poll':
                    endpoint = `/learning/delete/polls/${activityId}`;
                    break;
                case 'shortanswer':
                    endpoint = `/learning/delete/shortanswers/${activityId}`;
                    break;
                case 'wordcloud':
                    endpoint = `/learning/delete/wordclouds/${activityId}`;
                    break;
                default:
                    throw new Error(`Unknown activity type: ${type}`);
            }
            
            // Make the delete request
            const response = await this.api.delete(endpoint);
            
            if (response && response.message) {
                this.showNotification(response.message, 'success');
                
                // Refresh the current view
                this.refreshCurrentView();
                
                // If we're in a detail view, go back to overview
                if (this.currentView === 'detail') {
                    this.switchView('overview');
                }
            } else {
                throw new Error('Delete request failed');
            }
            
        } catch (error) {
            console.error(`Error deleting ${type} activity:`, error);
            this.showNotification(`Failed to delete ${type}: ${error.message}`, 'error');
        }
    }
}

// Initialize learning activities when DOM is ready
// Note: learningActivities is initialized in main.js to avoid conflicts