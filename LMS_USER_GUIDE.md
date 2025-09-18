# 🎓 COMP5241 Group 10 - Learning Management System

## Complete Backend-Frontend Integration Guide

### 🚀 Quick Start

1. **Start the System**:
   ```bash
   cd /workspaces/COMP5241_G10
   python start_system.py
   ```

2. **Access the System**:
   - **Login Page**: http://localhost:5000/login.html
   - **Main Application**: http://localhost:5000
   - **Backend API**: http://localhost:5000/api

### 🔐 Demo Users

#### Teachers (Full Access)
- **Username**: `teacher1`, **Password**: `password123`
- **Username**: `teacher2`, **Password**: `password123`

#### Students (Activity Access)
- **Username**: `student1`, **Password**: `password123`
- **Username**: `student2`, **Password**: `password123`
- **Username**: `student3`, **Password**: `password123`

### 🎯 Features Overview

## 📝 Learning Activities System

### 1. Quiz System
- **Create Quizzes**: Multiple choice, multiple select, and true/false questions
- **Time Limits**: Set time constraints for quiz completion
- **Automatic Scoring**: Real-time calculation of scores and feedback
- **Question Types**:
  - Multiple Choice (single correct answer)
  - Multiple Select (multiple correct answers)
  - True/False questions

**How to Use**:
1. Login as a teacher
2. Navigate to "Activities" → "Create New" → "Create Quiz"
3. Students can take quizzes from the "Overview" or "My Activities" section

### 2. Word Cloud System
- **Collaborative Word Collection**: Students submit words on specific topics
- **Real-time Visualization**: See word clouds update as submissions come in
- **Frequency Analysis**: Track which words are submitted most often
- **Submission Limits**: Control how many words each student can submit

**How to Use**:
1. Teachers create word cloud prompts
2. Students submit words related to the topic
3. View real-time word cloud visualization with frequency-based sizing

### 3. Short Answer Questions
- **Essay-Style Questions**: Open-ended questions for detailed responses
- **Teacher Feedback**: Personalized feedback and grading system
- **Batch Operations**: Grade multiple submissions efficiently
- **Analytics**: Track submission statistics and response quality

**How to Use**:
1. Teachers create short answer questions with hints and example answers
2. Students submit detailed text responses
3. Teachers provide feedback and scores
4. Students can view their graded responses and feedback

### 4. Mini Games System
- **Interactive Learning**: Educational games with scoring
- **Multiple Game Types**: Matching, sorting, sequence, and memory games
- **Leaderboards**: Competitive scoring with time-based rankings
- **Flexible Configuration**: Customizable game parameters

**How to Use**:
1. Teachers create games with specific learning objectives
2. Students play games and compete for high scores
3. View leaderboards and track progress

## 🖥️ User Interface Features

### Navigation
- **Dashboard**: Overview of all system activities
- **Activities**: Complete learning activities management
- **Courses**: Course organization (framework ready)
- **AI Assistant**: GenAI integration (framework ready)

### Activity Views
- **Overview**: Browse all available learning activities by type
- **My Activities**: View your personal learning progress
- **Create New**: Teacher interface for creating activities

### Responsive Design
- Mobile-friendly interface
- Bootstrap 5 styling
- Smooth animations and transitions
- Intuitive user experience

## 🔧 Technical Architecture

### Backend (Flask)
- **API Endpoints**: RESTful API for all learning activities
- **Authentication**: JWT-based user authentication
- **Database**: MongoDB with MongoEngine ODM
- **Validation**: Comprehensive input validation and error handling
- **Logging**: Detailed logging for debugging and monitoring

### Frontend (HTML/CSS/JavaScript)
- **Single Page Application**: Dynamic content loading
- **Modular Architecture**: Separate managers for different features
- **API Integration**: Complete backend API integration
- **Error Handling**: Graceful error handling with user notifications
- **Local Storage**: Client-side state management

### Key Components

#### Backend Models (`activities.py`)
- `Quiz`, `QuizQuestion`, `QuizOption`, `QuizAttempt`
- `WordCloud`, `WordCloudSubmission`
- `ShortAnswerQuestion`, `ShortAnswerSubmission`
- `MiniGame`, `MiniGameScore`

#### Frontend Managers
- `LearningActivitiesManager`: Complete frontend integration
- `APIClient`: Backend communication
- Authentication and session management

#### API Endpoints
```
/api/learning/quizzes/          - Quiz management
/api/learning/wordclouds/       - Word cloud management
/api/learning/shortanswers/     - Short answer management
/api/learning/minigames/        - Mini game management
/api/security/login            - User authentication
/api/health                    - System health check
```

## 🎮 How to Use the System

### For Students:

1. **Login**: Use demo credentials (student1/password123)
2. **Browse Activities**: View available quizzes, word clouds, questions, and games
3. **Participate**: 
   - Take quizzes and get immediate feedback
   - Submit words for collaborative word clouds
   - Answer short questions and receive teacher feedback
   - Play educational games and compete on leaderboards
4. **Track Progress**: View your activity history in "My Activities"

### For Teachers:

1. **Login**: Use demo credentials (teacher1/password123)
2. **Create Activities**:
   - Design comprehensive quizzes with multiple question types
   - Set up collaborative word cloud exercises
   - Create thought-provoking short answer questions
   - Build engaging educational mini-games
3. **Monitor Progress**: View student submissions and provide feedback
4. **Grade Work**: Use the feedback system for short answers

## 🌟 Key Achievements

### ✅ Complete Integration
- Backend APIs fully connected to frontend interface
- Real-time data synchronization
- Seamless user experience

### ✅ Production-Ready Features
- Authentication and authorization
- Input validation and error handling
- Responsive design for all devices
- Comprehensive logging and debugging

### ✅ Educational Value
- Multiple learning activity types
- Interactive and engaging interfaces
- Progress tracking and analytics
- Teacher-student feedback loops

### ✅ Scalable Architecture
- Modular design for easy expansion
- Clean separation of concerns
- RESTful API design
- Flexible database structure

## 🔮 Future Enhancements

- Real-time collaboration features
- Advanced analytics and reporting
- Mobile app development
- Integration with external learning platforms
- AI-powered content suggestions
- Video and multimedia support

## 🛠️ Development Notes

### File Structure
```
/workspaces/COMP5241_G10/
├── backend/
│   ├── app/
│   │   └── modules/learning_activities/
│   │       ├── activities.py          # Data models
│   │       ├── quizzes_routes.py      # Quiz API endpoints
│   │       ├── wordclouds_routes.py   # Word cloud endpoints
│   │       ├── shortanswers_routes.py # Short answer endpoints
│   │       └── minigames_routes.py    # Mini game endpoints
│   └── app.py                         # Main Flask application
├── frontend/
│   ├── index.html                     # Main application page
│   ├── login.html                     # Login page
│   └── static/
│       ├── js/
│       │   ├── learning-activities.js # Frontend integration
│       │   ├── api.js                 # API client
│       │   └── main.js                # Main application logic
│       └── css/
│           └── components.css         # Activity styling
└── start_system.py                    # System startup script
```

This integration provides a complete, functional learning management system with backend-frontend integration, user authentication, and comprehensive learning activities!

---

**COMP5241 Group 10 Team**: Joyce, Charlie, Sunny, Keith, Ting