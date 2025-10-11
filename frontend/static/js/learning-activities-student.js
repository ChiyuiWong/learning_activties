/*
COMP5241 Group 10 - Learning Activities Frontend (Student Version)
Student-specific implementation for learning activities functionality
*/

// Global notification function that delegates to the instance if available
function showNotification(message, type = 'info') {
    // If we have a global instance of StudentLearningActivities, use it
    if (window.studentLearningActivities) {
        window.studentLearningActivities.showNotification(message, type);
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

// Student Learning Activities Manager
class StudentLearningActivitiesManager {
    constructor(apiClient) {
        this.api = apiClient;
        this.currentView = 'overview';
        this.currentActivity = null;
        this.stats = {
            total: 0,
            completed: 0,
            pending: 0,
            byType: {}
        };
        
        // Call initialization functions
        this.init();
        this.setupRefreshInterval();
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

    // Basic poll participation view
    showPollInterface(poll) {
        const content = document.getElementById('activity-details-content');
        let html = `
            <div class="card">
                <div class="card-header">
                    <h5 class="mb-0">📊 ${poll.question}</h5>
                </div>
                <div class="card-body">
                    <form id="poll-response-form">
                        <ul class="list-group mb-3">
                            ${poll.options.map((opt, idx) => `
                                <li class="list-group-item">
                                    <div class="form-check">
                                        <input class="form-check-input" type="radio" name="poll_option" 
                                               value="${idx}" id="poll_option_${idx}" ${poll.userResponse === idx ? 'checked' : ''}>
                                        <label class="form-check-label" for="poll_option_${idx}">${opt.text}</label>
                                    </div>
                                </li>`).join('')}
                        </ul>
                        <div class="d-flex gap-2">
                            <button type="submit" class="btn btn-primary" ${poll.userResponse !== null ? 'disabled' : ''}>
                                ${poll.userResponse !== null ? 'Submitted' : 'Submit Answer'}
                            </button>
                            <button type="button" class="btn btn-outline-secondary" onclick="studentLearningActivities.switchView('overview')">
                                Back to Overview
                            </button>
                        </div>
                    </form>
                    ${poll.userResponse !== null ? `
                    <div class="mt-4">
                        <h6>Current Results</h6>
                        <div class="poll-results">
                            ${poll.options.map((opt, idx) => `
                                <div class="mb-2">
                                    <div class="d-flex justify-content-between mb-1">
                                        <span>${opt.text}</span>
                                        <span>${opt.votes || 0} votes</span>
                                    </div>
                                    <div class="progress">
                                        <div class="progress-bar" role="progressbar" 
                                             style="width: ${poll.totalVotes > 0 ? (opt.votes / poll.totalVotes) * 100 : 0}%" 
                                             aria-valuenow="${opt.votes || 0}" aria-valuemin="0" aria-valuemax="${poll.totalVotes || 1}">
                                        </div>
                                    </div>
                                </div>`).join('')}
                        </div>
                    </div>` : ''}
                </div>
            </div>
        `;
        
        content.innerHTML = html;
        
        // Add event listener for form submission
        const form = document.getElementById('poll-response-form');
        if (form && poll.userResponse === null) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const selectedOption = form.querySelector('input[name="poll_option"]:checked');
                
                if (!selectedOption) {
                    this.showNotification('Please select an option', 'warning');
                    return;
                }
                
                try {
                    const response = await this.api.post(`/learning/polls/${poll.id}/vote`, {
                        option_index: parseInt(selectedOption.value)
                    });
                    
                    if (response.success) {
                        this.showNotification('Vote submitted successfully!', 'success');
                        // Refresh the poll view
                        this.showActivityDetails('poll', poll.id);
                    } else {
                        throw new Error(response.error || 'Failed to submit vote');
                    }
                } catch (error) {
                    console.error('Error submitting poll vote:', error);
                    this.showNotification(error.message || 'Failed to submit vote', 'error');
                }
            });
        }
    }

    // Basic quiz view
    showQuizInterface(quiz) {
        const content = document.getElementById('activity-details-content');
        
        // Check if the quiz is completed or in progress
        const quizStatus = quiz.user_status || 'not_started';
        
        if (quizStatus === 'completed') {
            // Show quiz results
            content.innerHTML = `
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">📝 ${quiz.title} - Results</h5>
                    </div>
                    <div class="card-body">
                        <div class="text-center mb-4">
                            <div class="display-4 mb-2">${quiz.user_score}%</div>
                            <div class="badge ${quiz.user_passed ? 'bg-success' : 'bg-danger'} p-2">
                                ${quiz.user_passed ? 'Passed' : 'Failed'}
                            </div>
                            <p class="mt-2">
                                You answered ${quiz.user_correct_answers} out of ${quiz.questions.length} questions correctly.
                            </p>
                        </div>
                        
                        <h6 class="border-bottom pb-2 mb-3">Question Review</h6>
                        <div class="quiz-review">
                            ${quiz.questions.map((q, idx) => `
                                <div class="card mb-3 ${q.correct ? 'border-success' : 'border-danger'}">
                                    <div class="card-header bg-light">
                                        <div class="d-flex justify-content-between">
                                            <span>Question ${idx + 1}</span>
                                            <span class="badge ${q.correct ? 'bg-success' : 'bg-danger'}">
                                                ${q.correct ? 'Correct' : 'Incorrect'}
                                            </span>
                                        </div>
                                    </div>
                                    <div class="card-body">
                                        <p class="fw-medium">${q.text}</p>
                                        <ul class="list-group mb-3">
                                            ${q.options.map((opt, optIdx) => `
                                                <li class="list-group-item ${optIdx === q.correct_answer ? 'list-group-item-success' : ''} 
                                                                        ${optIdx === q.user_answer && optIdx !== q.correct_answer ? 'list-group-item-danger' : ''}">
                                                    ${opt}
                                                    ${optIdx === q.correct_answer ? ' <i class="bi bi-check-circle-fill text-success"></i>' : ''}
                                                    ${optIdx === q.user_answer && optIdx !== q.correct_answer ? ' <i class="bi bi-x-circle-fill text-danger"></i>' : ''}
                                                </li>
                                            `).join('')}
                                        </ul>
                                        ${q.explanation ? `<div class="explanation text-muted"><small>${q.explanation}</small></div>` : ''}
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        
                        <div class="text-center mt-4">
                            <button class="btn btn-outline-primary" onclick="studentLearningActivities.switchView('overview')">
                                Back to Activities
                            </button>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Show quiz start view
            content.innerHTML = `
                <div class="card">
                    <div class="card-header bg-primary text-white">
                        <h5 class="mb-0">📝 ${quiz.title}</h5>
                    </div>
                    <div class="card-body">
                        <div class="mb-4">
                            <h6 class="fw-bold">Quiz Information</h6>
                            <ul class="list-unstyled">
                                <li><i class="bi bi-question-circle me-2"></i> ${quiz.questions.length} Questions</li>
                                <li><i class="bi bi-clock me-2"></i> ${quiz.time_limit ? `${quiz.time_limit} minutes` : 'No time limit'}</li>
                                <li><i class="bi bi-trophy me-2"></i> Passing Score: ${quiz.passing_score || 60}%</li>
                            </ul>
                            
                            <p>${quiz.description}</p>
                            
                            <div class="alert alert-info">
                                <i class="bi bi-info-circle me-2"></i> 
                                ${quizStatus === 'in_progress' ? 
                                    'You have a quiz in progress. Continue where you left off.' : 
                                    'Once you start the quiz, answer all questions and submit before the time runs out.'}
                            </div>
                        </div>
                        
                        <div class="text-center">
                            <button class="btn btn-primary" onclick="studentLearningActivities.startQuiz('${quiz.id}')">
                                ${quizStatus === 'in_progress' ? 'Continue Quiz' : 'Start Quiz'}
                            </button>
                            <button class="btn btn-outline-secondary" onclick="studentLearningActivities.switchView('overview')">
                                Back to Activities
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    // Start quiz
    async startQuiz(quizId) {
        try {
            const content = document.getElementById('activity-details-content');
            content.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading quiz questions...</p>
                </div>
            `;
            
            const quiz = await this.api.get(`/learning/quizzes/${quizId}`);
            const quizSession = await this.api.post(`/learning/quizzes/${quizId}/start`, {});
            
            if (!quiz || !quizSession) {
                throw new Error('Failed to start quiz');
            }
            
            // Set up quiz session
            this.renderQuizSession(quiz, quizSession);
            
        } catch (error) {
            console.error('Error starting quiz:', error);
            this.showNotification('Failed to start quiz. Please try again.', 'error');
        }
    }

    // Render quiz session with questions
    renderQuizSession(quiz, session) {
        const content = document.getElementById('activity-details-content');
        const timeLimit = quiz.time_limit * 60; // convert to seconds
        const endTime = new Date(session.start_time).getTime() + (timeLimit * 1000);
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header bg-primary text-white">
                    <div class="d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">📝 ${quiz.title}</h5>
                        <div id="quiz-timer" class="bg-light text-dark px-3 py-1 rounded">
                            ${timeLimit ? 'Time Remaining: <span id="time-remaining">Loading...</span>' : 'No time limit'}
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <form id="quiz-form">
                        <div class="quiz-progress mb-4">
                            <div class="progress">
                                <div id="quiz-progress-bar" class="progress-bar" role="progressbar" style="width: 0%" 
                                     aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                            <div class="d-flex justify-content-between mt-1">
                                <small>Question <span id="current-question">1</span> of ${session.questions.length}</small>
                                <small><span id="answered-count">0</span> answered</small>
                            </div>
                        </div>
                        
                        <div id="quiz-questions-container">
                            ${session.questions.map((q, idx) => this.renderQuizQuestion(q, idx, idx === 0)).join('')}
                        </div>
                        
                        <div class="d-flex justify-content-between mt-4">
                            <button type="button" class="btn btn-outline-secondary" id="prev-question" disabled>
                                Previous
                            </button>
                            <button type="button" class="btn btn-outline-primary" id="next-question">
                                Next
                            </button>
                        </div>
                        
                        <div class="text-center mt-4">
                            <button type="submit" class="btn btn-primary px-4" id="submit-quiz">
                                Submit Quiz
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        
        // Set up quiz navigation
        this.setupQuizNavigation(session.questions.length);
        
        // Set up quiz timer if there is a time limit
        if (timeLimit) {
            this.startQuizTimer(endTime, session.id);
        }
        
        // Set up form submission
        const form = document.getElementById('quiz-form');
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitQuiz(session.id);
        });
        
        // Store session data
        this.currentQuizSession = {
            id: session.id,
            quiz_id: quiz.id,
            questions: session.questions
        };
    }

    // Render a single quiz question
    renderQuizQuestion(question, index, isVisible) {
        return `
            <div class="quiz-question ${isVisible ? '' : 'd-none'}" data-question-index="${index}">
                <h5 class="mb-3">Question ${index + 1}</h5>
                <p class="fw-medium mb-3">${question.text}</p>
                
                <div class="options-list">
                    ${question.options.map((opt, optIdx) => `
                        <div class="form-check mb-2">
                            <input class="form-check-input" type="radio" name="question_${index}" 
                                   value="${optIdx}" id="q${index}_opt${optIdx}">
                            <label class="form-check-label" for="q${index}_opt${optIdx}">
                                ${opt}
                            </label>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    }

    // Set up quiz navigation
    setupQuizNavigation(questionCount) {
        let currentIndex = 0;
        const prevBtn = document.getElementById('prev-question');
        const nextBtn = document.getElementById('next-question');
        const currentQuestionDisplay = document.getElementById('current-question');
        const progressBar = document.getElementById('quiz-progress-bar');
        const questions = document.querySelectorAll('.quiz-question');
        const answeredCountDisplay = document.getElementById('answered-count');
        
        // Update progress function
        const updateProgress = () => {
            // Update current question display
            currentQuestionDisplay.textContent = currentIndex + 1;
            
            // Update progress bar
            progressBar.style.width = `${((currentIndex + 1) / questionCount) * 100}%`;
            progressBar.setAttribute('aria-valuenow', ((currentIndex + 1) / questionCount) * 100);
            
            // Count answered questions
            let answeredCount = 0;
            for (let i = 0; i < questionCount; i++) {
                const radioButtons = document.querySelectorAll(`input[name="question_${i}"]:checked`);
                if (radioButtons.length > 0) {
                    answeredCount++;
                }
            }
            answeredCountDisplay.textContent = answeredCount;
            
            // Update navigation buttons
            prevBtn.disabled = currentIndex === 0;
            nextBtn.textContent = currentIndex === questionCount - 1 ? "Review" : "Next";
        };
        
        // Next button click handler
        nextBtn.addEventListener('click', () => {
            if (currentIndex < questionCount - 1) {
                questions[currentIndex].classList.add('d-none');
                currentIndex++;
                questions[currentIndex].classList.remove('d-none');
                updateProgress();
            }
        });
        
        // Previous button click handler
        prevBtn.addEventListener('click', () => {
            if (currentIndex > 0) {
                questions[currentIndex].classList.add('d-none');
                currentIndex--;
                questions[currentIndex].classList.remove('d-none');
                updateProgress();
            }
        });
        
        // Listen for answer changes to update progress
        questions.forEach((q, idx) => {
            const radioButtons = q.querySelectorAll('input[type="radio"]');
            radioButtons.forEach(radio => {
                radio.addEventListener('change', updateProgress);
            });
        });
        
        // Initial progress update
        updateProgress();
    }

    // Start quiz timer
    startQuizTimer(endTime, sessionId) {
        const timerDisplay = document.getElementById('time-remaining');
        
        const updateTimer = () => {
            const now = new Date().getTime();
            const timeLeft = endTime - now;
            
            if (timeLeft <= 0) {
                // Time's up
                clearInterval(this.quizTimerInterval);
                timerDisplay.innerHTML = '00:00';
                timerDisplay.parentElement.classList.remove('bg-light');
                timerDisplay.parentElement.classList.add('bg-danger', 'text-white');
                
                this.showNotification('Time is up! Submitting your quiz...', 'warning');
                this.submitQuiz(sessionId);
            } else {
                // Update timer display
                const minutes = Math.floor((timeLeft / 1000) / 60);
                const seconds = Math.floor((timeLeft / 1000) % 60);
                
                timerDisplay.innerHTML = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                
                // Warning when less than 1 minute remaining
                if (timeLeft < 60000 && !timerDisplay.parentElement.classList.contains('bg-warning')) {
                    timerDisplay.parentElement.classList.remove('bg-light');
                    timerDisplay.parentElement.classList.add('bg-warning', 'text-dark');
                }
            }
        };
        
        // Initial update
        updateTimer();
        
        // Update every second
        this.quizTimerInterval = setInterval(updateTimer, 1000);
    }

    // Submit quiz answers
    async submitQuiz(sessionId) {
        // Get all answers
        const answers = [];
        const questions = this.currentQuizSession.questions;
        
        questions.forEach((question, idx) => {
            const selectedOption = document.querySelector(`input[name="question_${idx}"]:checked`);
            answers.push({
                question_id: question.id,
                selected_option_index: selectedOption ? parseInt(selectedOption.value) : null
            });
        });
        
        try {
            // Confirm submission if not all questions answered
            const unansweredCount = answers.filter(a => a.selected_option_index === null).length;
            
            if (unansweredCount > 0) {
                const confirmSubmit = confirm(`You have ${unansweredCount} unanswered question(s). Are you sure you want to submit?`);
                if (!confirmSubmit) {
                    return;
                }
            }
            
            const content = document.getElementById('activity-details-content');
            content.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Submitting your quiz...</p>
                </div>
            `;
            
            // Clear any running timer
            if (this.quizTimerInterval) {
                clearInterval(this.quizTimerInterval);
            }
            
            const response = await this.api.post(`/learning/quizzes/${this.currentQuizSession.quiz_id}/submit`, {
                session_id: sessionId,
                answers: answers
            });
            
            if (response && response.success) {
                this.showNotification('Quiz submitted successfully!', 'success');
                // Show quiz results
                this.showActivityDetails('quiz', this.currentQuizSession.quiz_id);
            } else {
                throw new Error(response.error || 'Failed to submit quiz');
            }
            
        } catch (error) {
            console.error('Error submitting quiz:', error);
            this.showNotification('Failed to submit quiz. Please try again.', 'error');
        }
    }

    // Word cloud participation view
    showWordCloudInterface(wordCloud) {
        const content = document.getElementById('activity-details-content');
        const userSubmitted = wordCloud.user_submissions && wordCloud.user_submissions.length > 0;
        const canSubmitMore = !wordCloud.max_submissions_reached;
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header bg-success text-white">
                    <h5 class="mb-0">☁️ ${wordCloud.title}</h5>
                </div>
                <div class="card-body">
                    <div class="mb-4">
                        <h6 class="fw-bold">Prompt</h6>
                        <p>${wordCloud.prompt}</p>
                        
                        ${wordCloud.user_submissions && wordCloud.user_submissions.length > 0 ? `
                        <div class="alert alert-info">
                            <h6>Your submissions</h6>
                            <p class="mb-0">${wordCloud.user_submissions.join(', ')}</p>
                        </div>` : ''}
                        
                        ${canSubmitMore ? `
                        <form id="wordcloud-form" class="mt-4">
                            <div class="mb-3">
                                <label for="word-submission" class="form-label">Enter your word or phrase</label>
                                <div class="input-group">
                                    <input type="text" class="form-control" id="word-submission" 
                                           placeholder="Enter a word or short phrase" maxlength="30" required>
                                    <button class="btn btn-primary" type="submit">Submit</button>
                                </div>
                                <small class="text-muted">
                                    ${wordCloud.max_submissions_per_user - (wordCloud.user_submissions ? wordCloud.user_submissions.length : 0)} 
                                    submission(s) remaining
                                </small>
                            </div>
                        </form>` : `
                        <div class="alert alert-warning">
                            <i class="bi bi-exclamation-circle me-2"></i>
                            You have reached the maximum number of submissions (${wordCloud.max_submissions_per_user}).
                        </div>`}
                    </div>
                    
                    <div class="wordcloud-container bg-light rounded p-4 text-center mb-4" style="min-height: 300px;">
                        <div id="wordcloud-visualization">
                            ${wordCloud.words && wordCloud.words.length > 0 ? '' : '<p class="text-muted">No submissions yet. Be the first to contribute!</p>'}
                        </div>
                    </div>
                    
                    <div class="text-center">
                        <button class="btn btn-primary me-2" onclick="studentLearningActivities.refreshWordCloud('${wordCloud.id}')">
                            Refresh
                        </button>
                        <button class="btn btn-outline-secondary" onclick="studentLearningActivities.switchView('overview')">
                            Back to Activities
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listener for word submission
        if (canSubmitMore) {
            const form = document.getElementById('wordcloud-form');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const wordInput = document.getElementById('word-submission');
                const word = wordInput.value.trim();
                
                if (!word) {
                    this.showNotification('Please enter a word or phrase', 'warning');
                    return;
                }
                
                try {
                    const response = await this.api.post(`/learning/wordclouds/${wordCloud.id}/submit`, {
                        word: word
                    });
                    
                    if (response.success) {
                        this.showNotification('Word submitted successfully!', 'success');
                        wordInput.value = '';
                        // Refresh the word cloud
                        this.showActivityDetails('wordcloud', wordCloud.id);
                    } else {
                        throw new Error(response.error || 'Failed to submit word');
                    }
                } catch (error) {
                    console.error('Error submitting word:', error);
                    this.showNotification(error.message || 'Failed to submit word', 'error');
                }
            });
        }
        
        // Render word cloud visualization if words exist
        if (wordCloud.words && wordCloud.words.length > 0) {
            this.renderWordCloudVisualization(wordCloud.words);
        }
    }

    // Refresh word cloud
    async refreshWordCloud(wordCloudId) {
        try {
            const wordCloud = await this.api.get(`/learning/wordclouds/${wordCloudId}`);
            this.showWordCloudInterface(wordCloud);
        } catch (error) {
            console.error('Error refreshing word cloud:', error);
            this.showNotification('Failed to refresh word cloud', 'error');
        }
    }

    // Render word cloud visualization using D3 and cloud layout
    renderWordCloudVisualization(words) {
        // This function would use D3.js and d3-cloud library to render the word cloud
        // We'll implement a simplified version for now
        const container = document.getElementById('wordcloud-visualization');
        
        // Clear previous content
        container.innerHTML = '';
        
        // Simple visualization - we'd use a proper library in production
        const maxCount = Math.max(...words.map(w => w.count));
        const minSize = 14;
        const maxSize = 50;
        
        words.forEach(word => {
            const size = minSize + ((word.count / maxCount) * (maxSize - minSize));
            const opacity = 0.5 + ((word.count / maxCount) * 0.5);
            
            const wordSpan = document.createElement('span');
            wordSpan.textContent = word.text;
            wordSpan.style.fontSize = `${size}px`;
            wordSpan.style.opacity = opacity;
            wordSpan.style.padding = '5px 10px';
            wordSpan.style.margin = '5px';
            wordSpan.style.display = 'inline-block';
            
            container.appendChild(wordSpan);
        });
    }

    // Short answer view and submission
    showShortAnswerInterface(shortAnswer) {
        const content = document.getElementById('activity-details-content');
        const userSubmitted = shortAnswer.user_submission && shortAnswer.user_submission.answer;
        const hasFeedback = userSubmitted && shortAnswer.user_submission.feedback;
        
        content.innerHTML = `
            <div class="card">
                <div class="card-header bg-info text-white">
                    <h5 class="mb-0">📄 ${shortAnswer.title}</h5>
                </div>
                <div class="card-body">
                    <div class="mb-4">
                        <h6 class="fw-bold">Question</h6>
                        <p>${shortAnswer.question}</p>
                        
                        ${shortAnswer.answer_guidelines ? `
                        <div class="alert alert-light border">
                            <h6>Answer Guidelines</h6>
                            <p class="mb-0">${shortAnswer.answer_guidelines}</p>
                        </div>` : ''}
                    </div>
                    
                    ${userSubmitted ? `
                        <div class="card bg-light mb-4">
                            <div class="card-header">
                                <h6 class="mb-0">Your Answer</h6>
                            </div>
                            <div class="card-body">
                                <p>${shortAnswer.user_submission.answer}</p>
                            </div>
                            ${hasFeedback ? `
                            <div class="card-footer">
                                <h6>Feedback</h6>
                                <div class="feedback-content">
                                    ${shortAnswer.user_submission.feedback}
                                </div>
                                ${shortAnswer.user_submission.score !== null ? `
                                <div class="mt-2 text-end">
                                    <span class="badge bg-primary">Score: ${shortAnswer.user_submission.score}/${shortAnswer.max_score || 100}</span>
                                </div>` : ''}
                            </div>` : `
                            <div class="card-footer text-muted">
                                <p class="text-muted">Your answer has been submitted and is waiting for teacher feedback.</p>
                            </div>`}
                        </div>
                    ` : `
                        <form id="shortanswer-form" class="mb-4">
                            <div class="mb-3">
                                <label for="answer-submission" class="form-label">Your Answer</label>
                                <textarea class="form-control" id="answer-submission" rows="6" 
                                          maxlength="${shortAnswer.max_length || 1000}" required></textarea>
                                <small class="text-muted">
                                    Maximum ${shortAnswer.max_length || 1000} characters
                                </small>
                            </div>
                            <button type="submit" class="btn btn-primary">Submit Answer</button>
                        </form>
                    `}
                    
                    <div class="text-center mt-4">
                        <button class="btn btn-outline-secondary" onclick="studentLearningActivities.switchView('overview')">
                            Back to Activities
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add event listener for answer submission
        if (!userSubmitted) {
            const form = document.getElementById('shortanswer-form');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const answerInput = document.getElementById('answer-submission');
                const answer = answerInput.value.trim();
                
                if (!answer) {
                    this.showNotification('Please enter your answer', 'warning');
                    return;
                }
                
                try {
                    const response = await this.api.post(`/learning/shortanswers/${shortAnswer.id}/submit`, {
                        answer: answer
                    });
                    
                    if (response.success) {
                        this.showNotification('Answer submitted successfully!', 'success');
                        // Refresh the short answer view
                        this.showActivityDetails('shortanswer', shortAnswer.id);
                    } else {
                        throw new Error(response.error || 'Failed to submit answer');
                    }
                } catch (error) {
                    console.error('Error submitting answer:', error);
                    this.showNotification(error.message || 'Failed to submit answer', 'error');
                }
            });
        }
    }

    // Display details for a specific activity
    async showActivityDetails(type, id) {
        console.log(`Showing details for ${type} with ID: ${id}`);
        this.currentActivity = { type, id };
        
        document.querySelectorAll('.activity-view').forEach(v => v.classList.add('d-none'));
        document.getElementById('activity-details').classList.remove('d-none');
        
        // Show loading state
        document.getElementById('activity-details-content').innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading activity details...</p>
            </div>
        `;
        
        try {
            let activity;
            
            // Fetch the appropriate activity type
            switch(type) {
                case 'poll':
                    activity = await this.api.get(`/learning/polls/${id}`);
                    this.showPollInterface(activity);
                    break;
                    
                case 'quiz':
                    activity = await this.api.get(`/learning/quizzes/${id}`);
                    this.showQuizInterface(activity);
                    break;
                    
                case 'wordcloud':
                    activity = await this.api.get(`/learning/wordclouds/${id}`);
                    this.showWordCloudInterface(activity);
                    break;
                    
                case 'shortanswer':
                    activity = await this.api.get(`/learning/shortanswers/${id}`);
                    this.showShortAnswerInterface(activity);
                    break;
                    
                default:
                    throw new Error(`Unknown activity type: ${type}`);
            }
            
        } catch (error) {
            console.error(`Error loading ${type} details:`, error);
            document.getElementById('activity-details-content').innerHTML = `
                <div class="alert alert-danger">
                    <h5>Error</h5>
                    <p>Failed to load activity details. Please try again later.</p>
                    <button class="btn btn-outline-secondary" onclick="studentLearningActivities.switchView('overview')">
                        Back to Activities
                    </button>
                </div>
            `;
        }
    }

    // Event binding for activity cards and navigation
    bindEventListeners() {
        // Delegate click events for activity cards
        document.addEventListener('click', (e) => {
            // Handle activity card clicks
            const activityCard = e.target.closest('[data-activity-id]');
            if (activityCard) {
                const type = activityCard.getAttribute('data-activity-type');
                const id = activityCard.getAttribute('data-activity-id');
                this.showActivityDetails(type, id);
            }
            
            // Handle navigation buttons
            const navButton = e.target.closest('[data-activity-view]');
            if (navButton) {
                const view = navButton.getAttribute('data-activity-view');
                this.switchView(view);
            }
        });
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
        }
    }
    
    refreshCurrentView() {
        // Refresh the current view based on what view is active
        console.log(`Refreshing current view: ${this.currentView}`);
        
        switch(this.currentView) {
            case 'overview':
                this.loadActivityCounts();
                this.loadActivitiesFeed();
                break;
                
            case 'my-activities':
                this.loadMyActivities();
                break;
                
            case 'activity-details':
                if (this.currentActivity) {
                    this.showActivityDetails(this.currentActivity.type, this.currentActivity.id);
                } else {
                    this.switchView('overview');
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
            
            // Update total counts
            this.stats.total = quizzes.length + wordclouds.length + shortanswers.length + polls.length;
            this.loadActivitiesFeed();
            
        } catch (error) {
            console.error('Error loading activity counts:', error);
            // Set error states
            ['quiz-count', 'wordcloud-count', 'shortanswer-count', 'poll-count'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.textContent = 'Error loading';
            });
        }
    }
    
    async loadActivitiesFeed() {
        const container = document.getElementById('activities-feed');
        if (!container) return;
        
        try {
            const courseId = 'COMP5241';
            
            // Get activities for each type and combine them
            const [quizzes, wordclouds, shortanswers, polls] = await Promise.all([
                this.api.get(`/learning/quizzes/?course_id=${courseId}`),
                this.api.get(`/learning/wordclouds/?course_id=${courseId}`),
                this.api.get(`/learning/shortanswers/?course_id=${courseId}`),
                this.api.get(`/learning/polls/?course_id=${courseId}`)
            ]);
            
            // Combine and sort by date
            const allActivities = [
                ...quizzes.map(a => ({ ...a, type: 'quiz' })),
                ...wordclouds.map(a => ({ ...a, type: 'wordcloud' })),
                ...shortanswers.map(a => ({ ...a, type: 'shortanswer' })),
                ...polls.map(a => ({ ...a, type: 'poll' }))
            ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            
            if (allActivities.length === 0) {
                container.innerHTML = `
                    <div class="text-center py-5">
                        <div class="display-1 text-muted mb-3">📋</div>
                        <p class="text-muted">No learning activities available yet.</p>
                    </div>
                `;
                return;
            }
            
            const getTypeInfo = (type) => {
                switch(type) {
                    case 'quiz': return { icon: '📝', name: 'Quiz', class: 'primary' };
                    case 'wordcloud': return { icon: '☁️', name: 'Word Cloud', class: 'success' };
                    case 'shortanswer': return { icon: '📄', name: 'Short Answer', class: 'info' };
                    case 'poll': return { icon: '📊', name: 'Poll', class: 'secondary' };
                    default: return { icon: '📌', name: 'Activity', class: 'dark' };
                }
            };
            
            // Generate HTML for feed
            container.innerHTML = `
                <div class="list-group">
                    ${allActivities.slice(0, 10).map(activity => {
                        const typeInfo = getTypeInfo(activity.type);
                        const date = new Date(activity.created_at).toLocaleDateString();
                        return `
                            <div class="list-group-item list-group-item-action d-flex align-items-center" 
                                 data-activity-id="${activity.id}" 
                                 data-activity-type="${activity.type}">
                                <div class="activity-icon me-3 p-2 rounded-circle bg-${typeInfo.class} bg-opacity-10">
                                    <span class="fs-5">${typeInfo.icon}</span>
                                </div>
                                <div class="flex-grow-1">
                                    <div class="d-flex justify-content-between align-items-center">
                                        <h6 class="mb-0">${activity.title}</h6>
                                        <span class="badge bg-${typeInfo.class} rounded-pill">${typeInfo.name}</span>
                                    </div>
                                    <small class="text-muted">${date}</small>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
            
        } catch (error) {
            console.error('Error loading activities feed:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    <p class="mb-0">Failed to load activities. Please try again later.</p>
                </div>
            `;
        }
    }
    
    async loadMyActivities() {
        const content = document.getElementById('my-activities-content');
        if (!content) return;
        
        content.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading your activities...</p>
            </div>
        `;
        
        try {
            const courseId = 'COMP5241'; // TODO: Get from current course context
            console.log('Loading student activities for course:', courseId);
            
            // Get all activities with student participation status
            const [quizzes, wordclouds, shortanswers, polls] = await Promise.all([
                this.api.get(`/learning/quizzes/student/?course_id=${courseId}`),
                this.api.get(`/learning/wordclouds/student/?course_id=${courseId}`),
                this.api.get(`/learning/shortanswers/student/?course_id=${courseId}`),
                this.api.get(`/learning/polls/student/?course_id=${courseId}`)
            ]);
            
            // Combine all activities
            const allActivities = [
                ...quizzes.map(a => ({ ...a, type: 'quiz' })),
                ...wordclouds.map(a => ({ ...a, type: 'wordcloud' })),
                ...shortanswers.map(a => ({ ...a, type: 'shortanswer' })),
                ...polls.map(a => ({ ...a, type: 'poll' }))
            ].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            
            // Group activities by status
            const completed = allActivities.filter(a => a.status === 'completed');
            const inProgress = allActivities.filter(a => a.status === 'in_progress');
            const notStarted = allActivities.filter(a => a.status === 'not_started');
            
            console.log('Activities loaded:', {
                completed: completed.length,
                inProgress: inProgress.length,
                notStarted: notStarted.length
            });
            
            // Update stats
            this.stats.completed = completed.length;
            this.stats.pending = inProgress.length + notStarted.length;
            
            const getTypeInfo = (type) => {
                switch(type) {
                    case 'quiz': return { icon: '📝', name: 'Quiz', class: 'primary' };
                    case 'wordcloud': return { icon: '☁️', name: 'Word Cloud', class: 'success' };
                    case 'shortanswer': return { icon: '📄', name: 'Short Answer', class: 'info' };
                    case 'poll': return { icon: '📊', name: 'Poll', class: 'secondary' };
                    default: return { icon: '📌', name: 'Activity', class: 'dark' };
                }
            };
            
            // Render the activities
            if (allActivities.length === 0) {
                content.innerHTML = `
                    <div class="text-center py-5">
                        <div class="display-1 text-muted mb-3">📋</div>
                        <p class="text-muted">You haven't participated in any activities yet.</p>
                    </div>
                `;
                return;
            }
            
            // Create activity cards
            const renderActivityCard = (activity) => {
                const typeInfo = getTypeInfo(activity.type);
                const date = new Date(activity.created_at).toLocaleDateString();
                let statusBadge = '';
                
                switch(activity.status) {
                    case 'completed':
                        statusBadge = `<span class="badge bg-success">Completed</span>`;
                        break;
                    case 'in_progress':
                        statusBadge = `<span class="badge bg-warning">In Progress</span>`;
                        break;
                    default:
                        statusBadge = `<span class="badge bg-secondary">Not Started</span>`;
                }
                
                let scoreInfo = '';
                if (activity.score !== undefined && activity.status === 'completed') {
                    scoreInfo = `
                        <div class="mt-1">
                            <small>Score: ${activity.score}%</small>
                            <div class="progress" style="height: 6px;">
                                <div class="progress-bar bg-${activity.passed ? 'success' : 'danger'}" role="progressbar" 
                                     style="width: ${activity.score}%" aria-valuenow="${activity.score}" 
                                     aria-valuemin="0" aria-valuemax="100"></div>
                            </div>
                        </div>
                    `;
                }
                
                return `
                    <div class="col-lg-4 col-md-6 mb-4">
                        <div class="card h-100 activity-card" 
                             data-activity-id="${activity.id}" 
                             data-activity-type="${activity.type}">
                            <div class="card-header bg-${typeInfo.class} bg-opacity-10 d-flex justify-content-between align-items-center">
                                <div>
                                    <span class="me-2">${typeInfo.icon}</span>
                                    <span class="fw-medium">${typeInfo.name}</span>
                                </div>
                                ${statusBadge}
                            </div>
                            <div class="card-body">
                                <h5 class="card-title">${activity.title}</h5>
                                <p class="card-text small text-muted">${activity.description || ''}</p>
                                ${scoreInfo}
                            </div>
                            <div class="card-footer bg-white">
                                <small class="text-muted">Created on ${date}</small>
                                <button class="btn btn-sm btn-outline-${typeInfo.class} float-end">
                                    ${activity.status === 'completed' ? 'View Results' : 'Continue'}
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            };
            
            content.innerHTML = `
                <div class="activity-stats row mb-4 text-center">
                    <div class="col-md-4">
                        <div class="card border-success">
                            <div class="card-body">
                                <h5 class="display-4 fw-bold text-success">${completed.length}</h5>
                                <p class="mb-0">Completed</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card border-warning">
                            <div class="card-body">
                                <h5 class="display-4 fw-bold text-warning">${inProgress.length}</h5>
                                <p class="mb-0">In Progress</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card border-secondary">
                            <div class="card-body">
                                <h5 class="display-4 fw-bold text-secondary">${notStarted.length}</h5>
                                <p class="mb-0">Not Started</p>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${inProgress.length > 0 ? `
                <div class="mb-4">
                    <h5>In Progress</h5>
                    <div class="row">
                        ${inProgress.map(renderActivityCard).join('')}
                    </div>
                </div>` : ''}
                
                ${notStarted.length > 0 ? `
                <div class="mb-4">
                    <h5>Not Started</h5>
                    <div class="row">
                        ${notStarted.map(renderActivityCard).join('')}
                    </div>
                </div>` : ''}
                
                ${completed.length > 0 ? `
                <div>
                    <h5>Completed</h5>
                    <div class="row">
                        ${completed.map(renderActivityCard).join('')}
                    </div>
                </div>` : ''}
            `;
            
        } catch (error) {
            console.error('Error loading my activities:', error);
            content.innerHTML = `
                <div class="alert alert-danger">
                    <p class="mb-0">Failed to load your activities. Please try again later.</p>
                </div>
            `;
        }
    }
    
    init() {
        console.log('Initializing Student Learning Activities Manager...');
        this.bindEventListeners();
        this.loadActivityCounts();
    }
}

// Initialize student learning activities when DOM is ready
let studentLearningActivities;
document.addEventListener('DOMContentLoaded', function() {
    // Wait for API client to be available
    setTimeout(() => {
        if (typeof api !== 'undefined') {
            studentLearningActivities = new StudentLearningActivitiesManager(api);
            console.log('Student Learning Activities Manager initialized');
        } else {
            console.error('API client not available for Student Learning Activities Manager');
        }
    }, 100);
});

// Helper functions
function formatTimeFromSeconds(seconds) {
    if (!seconds) return 'No time limit';
    return Math.ceil(seconds / 60);
}