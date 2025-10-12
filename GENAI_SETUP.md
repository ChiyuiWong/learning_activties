# GenAI Chatbot Setup Guide

## Overview
This guide explains how to set up and use the GenAI chatbot feature integrated with Ollama for local AI model management and RAG (Retrieval-Augmented Generation) capabilities.

## Prerequisites

### 1. Install Ollama
First, install Ollama on your system:
- Visit [https://ollama.ai](https://ollama.ai)
- Download and install Ollama for your operating system
- Verify installation by running: `ollama --version`

### 2. Install Python Dependencies
Install the required Python packages:
```bash
cd backend
pip install -r requirements.txt
```

### 3. Start Ollama Service
Start the Ollama service (this must be running for the chatbot to work):
```bash
ollama serve
```

## Features

### 1. Model Management
- **View Models**: See all available and downloaded Ollama models
- **Download Models**: Download new models like llama2, mistral, codellama
- **Model Selection**: Choose which model to use for conversations

### 2. Chat Interface
- **Real-time Chat**: Chat with AI models using a modern interface
- **Session Management**: Create and manage multiple chat sessions
- **Message History**: View conversation history across sessions

### 3. Course Materials Integration (RAG)
- **Upload Materials**: Teachers can upload PDF, DOCX, TXT, PPTX files
- **Content Processing**: Automatic text extraction and processing
- **Context-Aware Chat**: AI can answer questions based on uploaded materials

## Usage Instructions

### For Teachers

1. **Upload Course Materials**:
   - Go to AI Assistant → Course Materials tab
   - Click "Upload Material"
   - Fill in title, description, and course ID
   - Select and upload your file
   - Wait for processing to complete

2. **Create Contextual Chat**:
   - Go to AI Assistant → Chat tab
   - Select a model from dropdown
   - Choose course context (optional)
   - Select relevant materials for context
   - Start chatting with context-aware responses

### For Students

1. **Basic Chat**:
   - Go to AI Assistant → Chat tab
   - Select an available model
   - Type your question and press Enter or Ctrl+Enter
   - View AI responses in real-time

2. **Access Course Context**:
   - If teacher has uploaded materials, you can chat with course-specific context
   - Responses will be based on the course materials

## Model Recommendations

### Popular Models to Download:
- **llama2**: General-purpose conversational AI
- **mistral**: Fast and efficient for most tasks
- **codellama**: Specialized for programming questions
- **vicuna**: Good for detailed explanations
- **orca-mini**: Lightweight option for basic questions

### Download Command Examples:
```bash
# Via Web Interface (Recommended)
# Use the Models tab in the AI Assistant

# Via Command Line (Alternative)
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

## API Endpoints

### Model Management
- `GET /api/genai/models` - List available models
- `POST /api/genai/models/download` - Download a model

### Course Materials
- `GET /api/genai/materials` - List materials
- `POST /api/genai/materials/upload` - Upload material
- `DELETE /api/genai/materials/{id}` - Delete material

### Chat
- `GET /api/genai/chat/sessions` - List chat sessions
- `POST /api/genai/chat/sessions` - Create session
- `GET /api/genai/chat/sessions/{id}/messages` - Get messages
- `POST /api/genai/chat/sessions/{id}/messages` - Send message

## Troubleshooting

### Common Issues:

1. **"No models available"**:
   - Ensure Ollama is running: `ollama serve`
   - Download a model via the Models tab

2. **"Failed to load models"**:
   - Check if Ollama service is running
   - Verify Ollama is accessible at default port (11434)

3. **"Material upload failed"**:
   - Check file size (max 16MB)
   - Ensure file type is supported (PDF, DOCX, TXT, PPTX)
   - Verify you have teacher permissions

4. **"Chat not responding"**:
   - Ensure a model is selected
   - Check Ollama service status
   - Verify model is downloaded

## File Structure

```
backend/app/modules/genai/
├── models.py          # Database models
├── routes.py          # API endpoints
└── services.py        # Business logic

frontend/static/js/
└── genai.js          # Frontend JavaScript

uploads/course_materials/  # Uploaded files storage
```

## Configuration

### Environment Variables
Add to your `.env` file:
```env
# Optional: OpenAI API key for fallback
OPENAI_API_KEY=your_openai_key_here

# Ollama configuration (if needed)
OLLAMA_HOST=localhost
OLLAMA_PORT=11434
```

## Security Notes

- Course materials are stored securely on the server
- Only teachers can upload materials
- Users can only access their own chat sessions
- File uploads are validated for type and size

## Support

If you encounter issues:
1. Check Ollama service status
2. Verify all dependencies are installed
3. Check browser console for JavaScript errors
4. Review server logs for API errors

## Future Enhancements

- Support for more file types
- Advanced RAG with vector similarity search
- Model fine-tuning capabilities
- Export chat conversations
- Real-time collaboration features
