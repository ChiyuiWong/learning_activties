# COMP5241 Group 10 - Learning Management System

## Project Overview
This is a Learning Management System (LMS) developed by Group 10 for COMP5241. The system is built with Python 3.11, Flask backend, MongoDB database, and a responsive frontend.

## Team Members & Responsibilities

| Member | Responsibilities | Modules |
|--------|-----------------|---------|
| **Ting** | GenAI integration and AI-powered features | `/backend/app/modules/genai/` |
| **Sunny** | Security, authentication, and admin panel | `/backend/app/modules/security/`, `/backend/app/modules/admin/` |
| **Joyce** | UI/UX design and frontend development | `/frontend/` |
| **Charlie** | Learning activities and student progress | `/backend/app/modules/learning_activities/` |
| **Keith** | Course management and teacher tools | `/backend/app/modules/courses/` |

## Technology Stack

### Backend
- **Python 3.11**
- **Flask** - Web framework
- **MongoDB** - Database
- **MongoEngine** - ODM (Object Document Mapper)
- **Flask-JWT-Extended** - Authentication
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5, CSS3, JavaScript**
- **Bootstrap 5** - UI framework (can be customized by Joyce)
- **Responsive Design**

### Database
- **MongoDB** - NoSQL document database
- **Indexed collections** for optimal performance

## Project Structure

```
COMP5241_G10/
├── backend/                    # Flask backend application
│   ├── app/
│   │   ├── __init__.py        # Flask app factory
│   │   ├── modules/           # Feature modules
│   │   │   ├── genai/         # AI features (Ting)
│   │   │   ├── security/      # Auth & security (Sunny)
│   │   │   ├── admin/         # Admin panel (Sunny)
│   │   │   ├── courses/       # Course management (Keith)
│   │   │   └── learning_activities/ # Activities (Charlie)
│   │   └── config/            # Configuration files
│   ├── config/
│   │   ├── config.py          # App configuration
│   │   └── database.py        # Database setup
│   ├── tests/                 # Unit tests
│   ├── requirements.txt       # Python dependencies
│   ├── app.py                # Application entry point
│   └── env.example           # Environment variables example
├── frontend/                  # Frontend application
│   ├── static/
│   │   ├── css/              # Stylesheets (Joyce)
│   │   ├── js/               # JavaScript files
│   │   └── images/           # Static images
│   ├── templates/            # HTML templates (if using Flask templating)
│   └── index.html           # Main application page
├── database/                 # Database scripts and documentation
│   ├── init_db.py           # Database initialization
│   ├── backup_db.py         # Backup script
│   └── README.md            # Database documentation
├── docs/                    # Project documentation
├── progress_report.md       # Team progress tracking
└── README.md               # This file
```

## Quick Start

### Prerequisites
- Python 3.11 or higher
- MongoDB (local installation or cloud service)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd COMP5241_G10
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Set Up Environment Variables
```bash
# Copy example environment file
cp env.example .env

# Edit .env file with your configuration
# Required variables:
# - SECRET_KEY
# - JWT_SECRET_KEY  
# - MONGODB_URI
# - OPENAI_API_KEY (for GenAI features)
```

#### Initialize Database
```bash
cd ../database
python init_db.py
```

#### Start Backend Server
```bash
cd ../backend
python app.py
```

The backend will be available at `http://localhost:5000`

### 3. Frontend Setup

#### Open Frontend
```bash
cd frontend
```

For development, you can:
- Open `index.html` directly in a browser, or
- Use a local HTTP server:

```bash
# Using Python
python -m http.server 3000

# Using Node.js (if you have it)
npx http-server -p 3000

# Using PHP (if you have it)
php -S localhost:3000
```

The frontend will be available at `http://localhost:3000`

### 4. Verify Installation

1. **Backend Health Check**: Visit `http://localhost:5000/api/health`
2. **Frontend**: Open `http://localhost:3000` in your browser
3. **Database**: Check MongoDB connection in the backend logs

## Development Workflow

### For Each Team Member

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-module-name
   ```

2. **Work on your assigned module**:
   - Ting: Implement GenAI features in `/backend/app/modules/genai/`
   - Sunny: Implement security in `/backend/app/modules/security/` and `/backend/app/modules/admin/`
   - Joyce: Design UI/UX in `/frontend/`
   - Charlie: Implement learning activities in `/backend/app/modules/learning_activities/`
   - Keith: Implement course management in `/backend/app/modules/courses/`

3. **Test your changes**:
   ```bash
   # Backend tests
   cd backend
   python -m pytest tests/
   
   # Manual testing
   # Test your API endpoints and frontend features
   ```

4. **Commit and push**:
   ```bash
   git add .
   git commit -m "Add: [feature description]"
   git push origin feature/your-module-name
   ```

5. **Create pull request** for review

### API Development

Each module has its own API endpoints:

- **Main**: `http://localhost:5000/api/health`
- **GenAI** (Ting): `http://localhost:5000/api/genai/*`
- **Security** (Sunny): `http://localhost:5000/api/security/*`
- **Admin** (Sunny): `http://localhost:5000/api/admin/*`
- **Courses** (Keith): `http://localhost:5000/api/courses/*`
- **Learning Activities** (Charlie): `http://localhost:5000/api/learning/*`

### Database Collections

The system uses the following MongoDB collections:
- `users` - User accounts and authentication
- `courses` - Course information and metadata
- `course_enrollments` - Student-course relationships
- `learning_activities` - Learning activities and assignments
- `activity_submissions` - Student submissions and grades
- `ai_generations` - AI-generated content history
- `security_audit_logs` - Security events and audit trail
- `admin_actions` - Administrative actions log

## Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/ -v
```

### Frontend Testing
- Manual testing through the browser
- Each team member should test their module's integration

### API Testing
Use tools like Postman or curl to test API endpoints:

```bash
# Health check
curl http://localhost:5000/api/health

# Login (Sunny's module)
curl -X POST http://localhost:5000/api/security/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test"}'
```

## Deployment

### Environment Configuration
- **Development**: Use local MongoDB and Flask development server
- **Production**: Configure production database and use Gunicorn

### Production Setup
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Module-Specific Documentation

### GenAI Module (Ting)
- Location: `/backend/app/modules/genai/`
- Features: AI content generation, content analysis
- Dependencies: OpenAI API, LangChain
- TODO: Implement AI integration, content generation endpoints

### Security Module (Sunny)
- Location: `/backend/app/modules/security/` and `/backend/app/modules/admin/`
- Features: Authentication, authorization, user management, admin panel
- Dependencies: Flask-JWT-Extended, bcrypt
- TODO: Implement login/logout, user registration, admin features

### UI/Frontend (Joyce)
- Location: `/frontend/`
- Features: Responsive design, user interface
- Dependencies: Bootstrap 5 (customizable)
- TODO: Design and implement user-friendly interface

### Courses Module (Keith)
- Location: `/backend/app/modules/courses/`
- Features: Course creation, enrollment, course management
- Dependencies: MongoEngine
- TODO: Implement course CRUD operations, enrollment system

### Learning Activities Module (Charlie)
- Location: `/backend/app/modules/learning_activities/`
- Features: Activities, assignments, progress tracking
- Dependencies: MongoEngine
- TODO: Implement activity creation, submission system, grading

## Contributing

1. Follow the module responsibility assignments
2. Use consistent code style (Python PEP 8, JavaScript ES6+)
3. Write tests for your features
4. Update documentation when adding new features
5. Use meaningful commit messages

## Meeting Schedule

- **Next Meeting**: October 8, 2025
- **Regular Updates**: Weekly progress reports
- **Integration Testing**: Before final submission

## Support & Communication

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Team Communication**: [Add your preferred communication channel]
- **Documentation**: Keep this README updated with changes

## License

This project is for educational purposes as part of COMP5241 coursework.