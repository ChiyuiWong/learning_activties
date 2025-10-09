/*
COMP5241 Group 10 - Learning Activities Frontend
Complete integration with backend APIs
*/

// Learning Activities Manager
class LearningActivitiesManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.currentView = 'overview';
        this.currentActivity = null;
        this.userRole = 'student'; // Will be set from user data
        
        this.init();
    }

    // Basic poll view (show poll question and options, allow teacher to view results)
    showPollInterface(poll) {
        const content = document.getElementById('activity-details-content');
        let html = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">📊 ${poll.question}</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group mb-3">
                        ${poll.options.map((opt, idx) => `<li class="list-group-item">${idx+1}. ${opt.text} <span class="badge bg-secondary float-end">${opt.votes||0}</span></li>`).join('')}
                    </ul>
                    <div class="d-flex gap-2">
                        <button class="btn btn-primary" onclick="learningActivities.refreshCurrentView()">Refresh</button>
                    </div>
                </div>
            </div>
        `;
        content.innerHTML = html;
    }

    // Show create form for different types; add poll handling
    showCreateForm(type) {
        const content = document.getElementById('activity-details-content');
        if (type === 'poll') {
            content.innerHTML = `
                <div class="card">
                    <div class="card-header"><h5>Create Poll</h5></div>
                    <div class="card-body">
                        <div class="mb-3">
                            <label class="form-label">Question</label>
                            <input class="form-control" id="poll-question">
                        </div>
                        <div id="poll-options">
                            <div class="input-group mb-2"><input class="form-control poll-option" placeholder="Option 1"></div>
                            <div class="input-group mb-2"><input class="form-control poll-option" placeholder="Option 2"></div>
                        </div>
                        <button class="btn btn-sm btn-outline-secondary mb-3" id="add-option">Add Option</button>
                        <div>
                            <button class="btn btn-success" id="create-poll-btn">Create Poll</button>
                        </div>
                    </div>
                </div>
            `;

            // Add option handler
            document.getElementById('add-option').addEventListener('click', () => {
                const idx = document.querySelectorAll('.poll-option').length + 1;
                const div = document.createElement('div');
                div.className = 'input-group mb-2';
                div.innerHTML = `<input class="form-control poll-option" placeholder="Option ${idx}">`;
                document.getElementById('poll-options').appendChild(div);
            });

            // Create poll handler
            document.getElementById('create-poll-btn').addEventListener('click', async () => {
                const question = document.getElementById('poll-question').value.trim();
                const opts = Array.from(document.querySelectorAll('.poll-option')).map(el => el.value.trim()).filter(Boolean);
                if (!question || opts.length < 2) {
                    alert('Please provide a question and at least two options.');
                    return;
                }
                try {
                    const payload = { question, options: opts, course_id: 'COMP5241' };
                    const res = await this.api.post('/learning/polls', payload);
                    showNotification('Poll created', 'success');
                    this.openActivity('poll', res.poll_id || res.id || res._id);
                } catch (e) {
                    console.error('Create poll failed', e);
                    showNotification('Failed to create poll', 'error');
                }
            });
        } else {
            // fallback: existing create flow for other types
            const details = document.getElementById('activity-details-content');
            details.innerHTML = `<div class="alert alert-info">Create form for ${type} is not implemented yet.</div>`;
        }
    }
    
    init() {
        console.log('Initializing Learning Activities Manager...');
        this.bindEventListeners();
        this.loadActivityCounts();
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
                const type = e.target.closest('[data-create-type]').getAttribute('data-create-type');
                this.showCreateForm(type);
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
    
    async loadActivityCounts() {
        try {
            // Load counts for each activity type
            const courseId = 'COMP5241'; // TODO: Get from current course context
            
            const [quizzes, wordclouds, shortanswers, minigames] = await Promise.all([
                this.api.get(`/learning/quizzes/?course_id=${courseId}`),
                this.api.get(`/learning/wordclouds/?course_id=${courseId}`),
                this.api.get(`/learning/shortanswers/?course_id=${courseId}`),
                this.api.get(`/learning/minigames/?course_id=${courseId}`)
            ]);
            
            document.getElementById('quiz-count').textContent = `${quizzes.length} available`;
            document.getElementById('wordcloud-count').textContent = `${wordclouds.length} active`;
            document.getElementById('shortanswer-count').textContent = `${shortanswers.length} questions`;
            document.getElementById('minigame-count').textContent = `${minigames.length} games`;
            
        } catch (error) {
            console.error('Error loading activity counts:', error);
            // Set error states
            ['quiz-count', 'wordcloud-count', 'shortanswer-count', 'minigame-count'].forEach(id => {
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
            
            // Load all activity types
            const [quizzes, wordclouds, shortanswers, minigames] = await Promise.all([
                this.api.get(`/learning/quizzes/?course_id=${courseId}`),
                this.api.get(`/learning/wordclouds/?course_id=${courseId}`),
                this.api.get(`/learning/shortanswers/?course_id=${courseId}`),
                this.api.get(`/learning/minigames/?course_id=${courseId}`)
            ]);

            // Fetch polls as well
            const polls = await this.api.get(`/learning/polls/?course_id=${courseId}`);
            
            const activities = [
                ...quizzes.map(q => ({...q, type: 'quiz', icon: '📝', color: 'primary'})),
                ...wordclouds.map(w => ({...w, type: 'wordcloud', icon: '☁️', color: 'success'})),
                ...shortanswers.map(s => ({...s, type: 'shortanswer', icon: '📄', color: 'info'})),
                ...minigames.map(m => ({...m, type: 'minigame', icon: '🎮', color: 'warning'}))
                ,...polls.map(p => ({...p, type: 'poll', icon: '📊', color: 'secondary'}))
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
            content.innerHTML = `
                <div class="alert alert-danger">
                    <h6>Error Loading Activities</h6>
                    <p>Unable to load your activities. Please try refreshing the page.</p>
                    <button class="btn btn-outline-danger btn-sm" onclick="learningActivities.loadMyActivities()">
                        Try Again
                    </button>
                </div>
            `;
        }
    }
    
    getActivityTypeInfo(type) {
        const typeMap = {
            quiz: { name: 'Quizzes', icon: '📝' },
            wordcloud: { name: 'Word Clouds', icon: '☁️' },
            shortanswer: { name: 'Short Answers', icon: '📄' },
            minigame: { name: 'Mini Games', icon: '🎮' },
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
            minigame: 'warning',
            poll: 'secondary'
        };
        const color = colorMap[type] || 'secondary';
        
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
                            <button class="btn btn-${color}" onclick="learningActivities.openActivity('${type}', '${activity.id || activity._id}')">
                                ${type === 'quiz' ? 'Take Quiz' : type === 'wordcloud' ? 'Submit Words' : type === 'shortanswer' ? 'Answer' : type === 'poll' ? 'View Poll' : 'Play Game'}
                            </button>
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
            
            case 'minigame':
                const maxScore = activity.max_score || 100;
                const gameType = activity.game_type || 'Unknown';
                return `<small class="text-muted d-block">Type: ${gameType} • Max score: ${maxScore}</small>`;
            
            default:
                return '';
        }
    }
    
    async openActivity(type, activityId) {
        console.log(`Opening ${type} activity: ${activityId}`);
        
        try {
            // Load activity details
            const activity = await this.api.get(`/learning/${type}s/${activityId}`);
            this.currentActivity = { type, activity, id: activityId };
            
            // Show activity interface based on type
            switch(type) {
                case 'quiz':
                    this.showQuizInterface(activity);
                    break;
                case 'wordcloud':
                    this.showWordCloudInterface(activity);
                    break;
                case 'shortanswer':
                    this.showShortAnswerInterface(activity);
                    break;
                case 'minigame':
                    this.showMiniGameInterface(activity);
                    break;
            }
            
        } catch (error) {
            console.error(`Error opening ${type} activity:`, error);
            showNotification(`Error opening activity: ${error.message}`, 'error');
        }
    }
    
    showQuizInterface(quiz) {
        const content = document.getElementById('activity-details-content');
        
        let html = `
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
            // Start quiz attempt
            const attempt = await this.api.post(`/learning/quizzes/${quizId}/attempt`);
            
            // Load quiz questions
            const quiz = await this.api.get(`/learning/quizzes/${quizId}`);
            
            this.showQuizQuestions(quiz, attempt.attempt_id);
            
        } catch (error) {
            console.error('Error starting quiz:', error);
            showNotification('Error starting quiz: ' + error.message, 'error');
        }
    }
    
    showQuizQuestions(quiz, attemptId) {
        const content = document.getElementById('activity-details-content');
        
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
            const form = document.getElementById('quiz-form');
            const formData = new FormData(form);
            
            // Prepare answers
            const answers = [];
            const questions = document.querySelectorAll('.question-container');
            
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
            
            // Submit quiz
            const result = await this.api.post(`/learning/quizzes/${quizId}/submit`, {
                answers: answers
            });
            
            this.showQuizResults(result);
            
        } catch (error) {
            console.error('Error submitting quiz:', error);
            showNotification('Error submitting quiz: ' + error.message, 'error');
        }
    }
    
    showQuizResults(result) {
        const content = document.getElementById('activity-details-content');
        
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
        const content = document.getElementById('activity-details-content');
        
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
        
        // Simple word cloud visualization using CSS
        let html = '<div class="word-cloud">';
        words.forEach(wordData => {
            const frequency = wordData.frequency || 1;
            const fontSize = Math.min(12 + frequency * 4, 28); // Scale font size based on frequency
            html += `<span class="word-item" style="font-size: ${fontSize}px; margin: 5px;">${wordData.word}</span>`;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }
    
    async submitWord(wordcloudId) {
        const wordInput = document.getElementById('word-input');
        const word = wordInput.value.trim();
        
        if (!word) {
            showNotification('Please enter a word', 'warning');
            return;
        }
        
        try {
            const result = await this.api.post(`/learning/wordclouds/${wordcloudId}/submit`, {
                word: word
            });
            
            showNotification('Word submitted successfully!', 'success');
            wordInput.value = '';
            
            // Reload word cloud data
            this.loadWordCloudData(wordcloudId);
            
        } catch (error) {
            console.error('Error submitting word:', error);
            showNotification('Error submitting word: ' + error.message, 'error');
        }
    }
    
    showShortAnswerInterface(question) {
        const content = document.getElementById('activity-details-content');
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">📄 Short Answer Question</h5>
                </div>
                <div class="card-body">
                    <h6>Question:</h6>
                    <p class="lead">${question.question}</p>
                    
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
            showNotification('Please enter an answer', 'warning');
            return;
        }
        
        try {
            const result = await this.api.post(`/learning/shortanswers/${questionId}/submit`, {
                answer: answerText
            });
            
            showNotification('Answer submitted successfully!', 'success');
            
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
            showNotification('Error submitting answer: ' + error.message, 'error');
        }
    }
    
    showMiniGameInterface(game) {
        const content = document.getElementById('activity-details-content');
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">🎮 ${game.title}</h5>
                    <p class="mb-0 text-muted">${game.description}</p>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h6>Instructions:</h6>
                            <p>${game.instructions || 'Follow the game prompts to play.'}</p>
                            
                            <div class="alert alert-warning">
                                <strong>Game Type:</strong> ${game.game_type}<br>
                                <strong>Maximum Score:</strong> ${game.max_score} points
                            </div>
                            
                            <button class="btn btn-warning btn-lg" onclick="learningActivities.startMiniGame('${game.id || game._id}')">
                                Start Game
                            </button>
                        </div>
                        <div class="col-md-4">
                            <h6>Leaderboard</h6>
                            <div id="game-leaderboard">
                                <p class="text-muted">Loading leaderboard...</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Load leaderboard
        this.loadGameLeaderboard(game.id || game._id);
    }
    
    async loadGameLeaderboard(gameId) {
        try {
            const leaderboard = await this.api.get(`/learning/minigames/${gameId}/leaderboard`);
            
            const container = document.getElementById('game-leaderboard');
            
            if (!leaderboard || leaderboard.length === 0) {
                container.innerHTML = '<p class="text-muted">No scores yet. Be the first to play!</p>';
                return;
            }
            
            let html = '<ol class="list-group list-group-numbered">';
            leaderboard.slice(0, 5).forEach(entry => {
                html += `
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">${entry.student_id}</div>
                            ${entry.time_taken ? `${entry.time_taken.toFixed(1)}s` : ''}
                        </div>
                        <span class="badge bg-primary rounded-pill">${entry.score}</span>
                    </li>
                `;
            });
            html += '</ol>';
            
            container.innerHTML = html;
            
        } catch (error) {
            console.error('Error loading leaderboard:', error);
            document.getElementById('game-leaderboard').innerHTML = 
                '<p class="text-muted">Error loading leaderboard</p>';
        }
    }
    
    async startMiniGame(gameId) {
        // This would implement the actual game logic based on game type
        showNotification('Mini-game functionality is being developed!', 'info');
        console.log(`Starting mini-game: ${gameId}`);
    }
    
    showCreateForm(type) {
        console.log(`Showing create form for: ${type}`);
        // This would show the creation form for the specific activity type
        showNotification(`${type} creation form is being developed!`, 'info');
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
}

// Initialize learning activities when DOM is ready
let learningActivities;
document.addEventListener('DOMContentLoaded', function() {
    // Wait for API client to be available
    setTimeout(() => {
        if (typeof api !== 'undefined') {
            learningActivities = new LearningActivitiesManager(api);
            console.log('Learning Activities Manager initialized');
        } else {
            console.error('API client not available for Learning Activities Manager');
        }
    }, 100);
});