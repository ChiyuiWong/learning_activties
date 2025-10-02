/*
COMP5241 Group 10 - GenAI Module JavaScript
Responsible: Ting
*/

// GenAI Module
const GenAI = {
    currentSession: null,
    currentModel: null,
    selectedMaterials: [],
    
    // Initialize the GenAI module
    init() {
        console.log('Initializing GenAI module...');
        
        // Bind event listeners
        this.bindEventListeners();
        
        // Load initial data
        this.loadModels();
        this.loadChatSessions();
        this.loadMaterials();
    },
    
    // Bind all event listeners
    bindEventListeners() {
        // View switcher
        document.querySelectorAll('[data-genai-view]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.target.getAttribute('data-genai-view');
                this.showView(view);
            });
        });
        
        // Model selection
        const modelSelect = document.getElementById('model-select');
        if (modelSelect) {
            modelSelect.addEventListener('change', (e) => {
                this.selectModel(e.target.value);
            });
        }
        
        // Message input
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                if (e.ctrlKey && e.key === 'Enter') {
                    this.sendMessage();
                }
            });
            
            messageInput.addEventListener('input', (e) => {
                const sendBtn = document.getElementById('send-message-btn');
                sendBtn.disabled = !e.target.value.trim() || !this.currentModel;
            });
        }
        
        // Send message button
        const sendBtn = document.getElementById('send-message-btn');
        if (sendBtn) {
            sendBtn.addEventListener('click', () => this.sendMessage());
        }
        
        // New chat button
        const newChatBtn = document.getElementById('new-chat-btn');
        if (newChatBtn) {
            newChatBtn.addEventListener('click', () => this.createNewChat());
        }
        
        // Clear chat button
        const clearChatBtn = document.getElementById('clear-chat-btn');
        if (clearChatBtn) {
            clearChatBtn.addEventListener('click', () => this.clearChat());
        }
        
        // Model management
        const refreshModelsBtn = document.getElementById('refresh-models-btn');
        if (refreshModelsBtn) {
            refreshModelsBtn.addEventListener('click', () => this.loadModels());
        }
        
        const downloadModelBtn = document.getElementById('download-model-btn');
        if (downloadModelBtn) {
            downloadModelBtn.addEventListener('click', () => this.downloadModel());
        }
        
        // Material upload
        const uploadMaterialBtn = document.getElementById('upload-material-btn');
        if (uploadMaterialBtn) {
            uploadMaterialBtn.addEventListener('click', () => this.showUploadModal());
        }
    },
    
    // Show specific view
    showView(viewName) {
        // Hide all views
        document.querySelectorAll('.genai-view').forEach(view => {
            view.classList.add('d-none');
        });
        
        // Show target view
        const targetView = document.getElementById(`genai-${viewName}`);
        if (targetView) {
            targetView.classList.remove('d-none');
        }
        
        // Update active button
        document.querySelectorAll('[data-genai-view]').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-genai-view="${viewName}"]`).classList.add('active');
        
        // Load view-specific data
        if (viewName === 'models') {
            this.loadModels();
        } else if (viewName === 'materials') {
            this.loadMaterials();
        }
    },
    
    // Load available models
    async loadModels() {
        try {
            const response = await fetch(`${app.apiBaseUrl}/genai/models`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateModelsList(data.models);
                this.updateModelSelect(data.models);
            } else {
                console.error('Failed to load models:', data.error);
                showAlert('Failed to load models: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error loading models:', error);
            showAlert('Error loading models. Please check if Ollama is running.', 'danger');
        }
    },
    
    // Update models list in models view
    updateModelsList(models) {
        const modelsTable = document.getElementById('models-table');
        if (!modelsTable) return;
        
        if (models.length === 0) {
            modelsTable.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-download" style="font-size: 3rem;"></i>
                    <p>No models downloaded yet</p>
                    <p class="small">Use the download form above to get started</p>
                </div>
            `;
            return;
        }
        
        let tableHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Model Name</th>
                            <th>Size</th>
                            <th>Status</th>
                            <th>Last Used</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        models.forEach(model => {
            const lastUsed = model.last_used ? 
                new Date(model.last_used).toLocaleDateString() : 
                'Never';
            
            const status = model.is_downloaded ? 
                '<span class="badge bg-success">Downloaded</span>' :
                '<span class="badge bg-warning">Available</span>';
            
            tableHTML += `
                <tr>
                    <td>
                        <strong>${model.name}</strong>
                    </td>
                    <td>${this.formatSize(model.size)}</td>
                    <td>${status}</td>
                    <td>${lastUsed}</td>
                    <td>
                        ${model.is_downloaded ? 
                            `<button class="btn btn-sm btn-primary" onclick="GenAI.selectModelInChat('${model.name}')">Use</button>` :
                            `<button class="btn btn-sm btn-success" onclick="GenAI.downloadSpecificModel('${model.name}')">Download</button>`
                        }
                    </td>
                </tr>
            `;
        });
        
        tableHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        modelsTable.innerHTML = tableHTML;
    },
    
    // Update model select dropdown
    updateModelSelect(models) {
        const modelSelect = document.getElementById('model-select');
        if (!modelSelect) return;
        
        const downloadedModels = models.filter(m => m.is_downloaded);
        
        modelSelect.innerHTML = '<option value="">Select a model...</option>';
        
        downloadedModels.forEach(model => {
            const option = document.createElement('option');
            option.value = model.name;
            option.textContent = `${model.name} (${this.formatSize(model.size)})`;
            modelSelect.appendChild(option);
        });
        
        if (downloadedModels.length === 0) {
            modelSelect.innerHTML = '<option value="">No models available - download from Models tab</option>';
        }
    },
    
    // Format file size
    formatSize(sizeStr) {
        if (!sizeStr) return 'Unknown';
        // If it's already formatted, return as is
        if (typeof sizeStr === 'string' && (sizeStr.includes('GB') || sizeStr.includes('MB'))) {
            return sizeStr;
        }
        // Convert bytes to readable format
        const bytes = parseInt(sizeStr);
        if (isNaN(bytes)) return sizeStr;
        
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    },
    
    // Download a model
    async downloadModel() {
        const modelName = document.getElementById('model-search').value.trim();
        if (!modelName) {
            showAlert('Please enter a model name', 'warning');
            return;
        }
        
        const downloadBtn = document.getElementById('download-model-btn');
        const originalText = downloadBtn.textContent;
        
        try {
            downloadBtn.disabled = true;
            downloadBtn.innerHTML = '<i class="bi bi-download"></i> Downloading...';
            
            const response = await fetch(`${app.apiBaseUrl}/genai/models/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({ model_name: modelName })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert(`Model ${modelName} downloaded successfully!`, 'success');
                document.getElementById('model-search').value = '';
                this.loadModels(); // Refresh models list
            } else {
                showAlert('Failed to download model: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error downloading model:', error);
            showAlert('Error downloading model. Please try again.', 'danger');
        } finally {
            downloadBtn.disabled = false;
            downloadBtn.textContent = originalText;
        }
    },
    
    // Download specific model from table
    async downloadSpecificModel(modelName) {
        try {
            const response = await fetch(`${app.apiBaseUrl}/genai/models/download`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({ model_name: modelName })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert(`Model ${modelName} downloaded successfully!`, 'success');
                this.loadModels();
            } else {
                showAlert('Failed to download model: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error downloading model:', error);
            showAlert('Error downloading model. Please try again.', 'danger');
        }
    },
    
    // Select model for chat
    selectModel(modelName) {
        this.currentModel = modelName;
        
        const chatModelInfo = document.getElementById('chat-model-info');
        const sendBtn = document.getElementById('send-message-btn');
        const messageInput = document.getElementById('message-input');
        
        if (modelName) {
            chatModelInfo.textContent = `Using ${modelName}`;
            sendBtn.disabled = !messageInput.value.trim();
            
            // Update model info
            const modelInfo = document.getElementById('model-info');
            if (modelInfo) {
                modelInfo.textContent = `Selected: ${modelName}`;
            }
        } else {
            chatModelInfo.textContent = 'Select a model to start chatting';
            sendBtn.disabled = true;
            
            const modelInfo = document.getElementById('model-info');
            if (modelInfo) {
                modelInfo.textContent = '';
            }
        }
    },
    
    // Select model from models view
    selectModelInChat(modelName) {
        const modelSelect = document.getElementById('model-select');
        if (modelSelect) {
            modelSelect.value = modelName;
            this.selectModel(modelName);
            this.showView('chat');
        }
    },
    
    // Create new chat session
    async createNewChat() {
        if (!this.currentModel) {
            showAlert('Please select a model first', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${app.apiBaseUrl}/genai/chat/sessions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({
                    model_name: this.currentModel,
                    context_materials: this.selectedMaterials
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession = data.session.id;
                this.clearChatMessages();
                this.loadChatSessions();
                showAlert('New chat session created!', 'success');
            } else {
                showAlert('Failed to create chat session: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error creating chat session:', error);
            showAlert('Error creating chat session. Please try again.', 'danger');
        }
    },
    
    // Send message
    async sendMessage() {
        const messageInput = document.getElementById('message-input');
        const message = messageInput.value.trim();
        
        if (!message || !this.currentModel) {
            return;
        }
        
        // Create session if needed
        if (!this.currentSession) {
            await this.createNewChat();
            if (!this.currentSession) return;
        }
        
        // Add user message to chat
        this.addMessageToChat('human', message);
        messageInput.value = '';
        
        // Disable send button
        const sendBtn = document.getElementById('send-message-btn');
        sendBtn.disabled = true;
        sendBtn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
        
        try {
            const response = await fetch(`${app.apiBaseUrl}/genai/chat/sessions/${this.currentSession}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Add AI response to chat
                this.addMessageToChat('ai', data.ai_response.content);
            } else {
                showAlert('Failed to send message: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            showAlert('Error sending message. Please try again.', 'danger');
        } finally {
            sendBtn.disabled = false;
            sendBtn.innerHTML = '<i class="bi bi-send"></i>';
        }
    },
    
    // Add message to chat interface
    addMessageToChat(type, content) {
        const chatMessages = document.getElementById('chat-messages');
        const messagesContainer = chatMessages.querySelector('.text-center');
        
        // Remove welcome message if present
        if (messagesContainer) {
            messagesContainer.remove();
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-3 ${type === 'human' ? 'text-end' : 'text-start'}`;
        
        const isUser = type === 'human';
        const bgClass = isUser ? 'bg-primary text-white' : 'bg-light';
        const alignment = isUser ? 'ms-auto' : 'me-auto';
        
        messageDiv.innerHTML = `
            <div class="d-inline-block p-3 rounded-3 ${bgClass} ${alignment}" style="max-width: 70%;">
                <div class="mb-1">
                    <small class="opacity-75">
                        <i class="bi bi-${isUser ? 'person-fill' : 'robot'}"></i>
                        ${isUser ? 'You' : this.currentModel}
                    </small>
                </div>
                <div>${this.formatMessage(content)}</div>
                <div class="mt-1">
                    <small class="opacity-50">${new Date().toLocaleTimeString()}</small>
                </div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    },
    
    // Format message content
    formatMessage(content) {
        // Simple markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    },
    
    // Clear chat messages
    clearChat() {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = `
            <div class="text-center text-muted mt-5">
                <i class="bi bi-chat-dots" style="font-size: 3rem;"></i>
                <p>Start a conversation with your AI assistant</p>
                <p class="small">Select a model above and type your message below</p>
            </div>
        `;
        this.currentSession = null;
    },
    
    // Clear chat messages only
    clearChatMessages() {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = `
            <div class="text-center text-muted mt-5">
                <i class="bi bi-chat-dots" style="font-size: 3rem;"></i>
                <p>Chat session ready</p>
                <p class="small">Type your message below to start the conversation</p>
            </div>
        `;
    },
    
    // Load chat sessions
    async loadChatSessions() {
        try {
            const response = await fetch(`${app.apiBaseUrl}/genai/chat/sessions`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateChatSessionsList(data.sessions);
            }
        } catch (error) {
            console.error('Error loading chat sessions:', error);
        }
    },
    
    // Update chat sessions list
    updateChatSessionsList(sessions) {
        const sessionsList = document.getElementById('chat-sessions-list');
        if (!sessionsList) return;
        
        sessionsList.innerHTML = '';
        
        if (sessions.length === 0) {
            sessionsList.innerHTML = `
                <div class="p-3 text-center text-muted">
                    <p class="small mb-0">No chat sessions yet</p>
                </div>
            `;
            return;
        }
        
        sessions.forEach(session => {
            const sessionItem = document.createElement('a');
            sessionItem.href = '#';
            sessionItem.className = 'list-group-item list-group-item-action';
            sessionItem.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <small class="mb-1">${session.model_name}</small>
                    <small>${new Date(session.updated_at).toLocaleDateString()}</small>
                </div>
                <p class="mb-1 small text-muted">
                    ${session.course_id ? `Course context` : 'General chat'}
                </p>
            `;
            
            sessionItem.addEventListener('click', (e) => {
                e.preventDefault();
                this.loadChatSession(session.id);
            });
            
            sessionsList.appendChild(sessionItem);
        });
    },
    
    // Load specific chat session
    async loadChatSession(sessionId) {
        try {
            const response = await fetch(`${app.apiBaseUrl}/genai/chat/sessions/${sessionId}/messages`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentSession = sessionId;
                this.displayChatHistory(data.messages);
            }
        } catch (error) {
            console.error('Error loading chat session:', error);
        }
    },
    
    // Display chat history
    displayChatHistory(messages) {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = '';
        
        if (messages.length === 0) {
            this.clearChatMessages();
            return;
        }
        
        messages.forEach(message => {
            this.addMessageToChat(message.message_type, message.content);
        });
    },
    
    // Load course materials
    async loadMaterials() {
        try {
            const response = await fetch(`${app.apiBaseUrl}/genai/materials`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.updateMaterialsList(data.materials);
            }
        } catch (error) {
            console.error('Error loading materials:', error);
        }
    },
    
    // Update materials list
    updateMaterialsList(materials) {
        const materialsTable = document.getElementById('materials-table');
        if (!materialsTable) return;
        
        if (materials.length === 0) {
            materialsTable.innerHTML = `
                <div class="text-center text-muted">
                    <i class="bi bi-file-earmark" style="font-size: 3rem;"></i>
                    <p>No course materials uploaded yet</p>
                    <p class="small">Click the Upload Material button to get started</p>
                </div>
            `;
            return;
        }
        
        let tableHTML = `
            <div class="table-responsive">
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Title</th>
                            <th>File Type</th>
                            <th>Size</th>
                            <th>Status</th>
                            <th>Uploaded</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        materials.forEach(material => {
            const status = material.is_processed ? 
                '<span class="badge bg-success">Processed</span>' :
                '<span class="badge bg-warning">Processing</span>';
            
            tableHTML += `
                <tr>
                    <td>
                        <strong>${material.title}</strong>
                        ${material.description ? `<br><small class="text-muted">${material.description}</small>` : ''}
                    </td>
                    <td><span class="badge bg-secondary">${material.file_type.toUpperCase()}</span></td>
                    <td>${this.formatSize(material.file_size)}</td>
                    <td>${status}</td>
                    <td>${new Date(material.created_at).toLocaleDateString()}</td>
                    <td>
                        <button class="btn btn-sm btn-danger" onclick="GenAI.deleteMaterial('${material.id}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        tableHTML += `
                    </tbody>
                </table>
            </div>
        `;
        
        materialsTable.innerHTML = tableHTML;
    },
    
    // Show upload modal
    showUploadModal() {
        // Create modal HTML
        const modalHTML = `
            <div class="modal fade" id="uploadMaterialModal" tabindex="-1">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Upload Course Material</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="upload-material-form">
                                <div class="mb-3">
                                    <label for="material-title" class="form-label">Title *</label>
                                    <input type="text" class="form-control" id="material-title" required>
                                </div>
                                <div class="mb-3">
                                    <label for="material-description" class="form-label">Description</label>
                                    <textarea class="form-control" id="material-description" rows="3"></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="material-course" class="form-label">Course ID *</label>
                                    <input type="text" class="form-control" id="material-course" required 
                                           placeholder="Enter course identifier">
                                </div>
                                <div class="mb-3">
                                    <label for="material-file" class="form-label">File *</label>
                                    <input type="file" class="form-control" id="material-file" 
                                           accept=".pdf,.docx,.txt,.pptx" required>
                                    <div class="form-text">
                                        Supported formats: PDF, DOCX, TXT, PPTX (Max 16MB)
                                    </div>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="upload-material-submit">Upload</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Remove existing modal if any
        const existingModal = document.getElementById('uploadMaterialModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Add modal to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('uploadMaterialModal'));
        modal.show();
        
        // Bind upload handler
        document.getElementById('upload-material-submit').addEventListener('click', () => {
            this.uploadMaterial(modal);
        });
    },
    
    // Upload material
    async uploadMaterial(modal) {
        const form = document.getElementById('upload-material-form');
        const formData = new FormData();
        
        const title = document.getElementById('material-title').value.trim();
        const description = document.getElementById('material-description').value.trim();
        const courseId = document.getElementById('material-course').value.trim();
        const file = document.getElementById('material-file').files[0];
        
        if (!title || !courseId || !file) {
            showAlert('Please fill in all required fields', 'warning');
            return;
        }
        
        formData.append('title', title);
        formData.append('description', description);
        formData.append('course_id', courseId);
        formData.append('file', file);
        
        const submitBtn = document.getElementById('upload-material-submit');
        const originalText = submitBtn.textContent;
        
        try {
            submitBtn.disabled = true;
            submitBtn.textContent = 'Uploading...';
            
            const response = await fetch(`${app.apiBaseUrl}/genai/materials/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Material uploaded successfully!', 'success');
                modal.hide();
                this.loadMaterials();
            } else {
                showAlert('Failed to upload material: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error uploading material:', error);
            showAlert('Error uploading material. Please try again.', 'danger');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    },
    
    // Delete material
    async deleteMaterial(materialId) {
        if (!confirm('Are you sure you want to delete this material?')) {
            return;
        }
        
        try {
            const response = await fetch(`${app.apiBaseUrl}/genai/materials/${materialId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Material deleted successfully!', 'success');
                this.loadMaterials();
            } else {
                showAlert('Failed to delete material: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Error deleting material:', error);
            showAlert('Error deleting material. Please try again.', 'danger');
        }
    }
};

// Make GenAI globally available
window.GenAI = GenAI;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize GenAI when the section is shown
    const genaiSection = document.getElementById('genai-section');
    if (genaiSection && !genaiSection.classList.contains('d-none')) {
        GenAI.init();
    }
});
