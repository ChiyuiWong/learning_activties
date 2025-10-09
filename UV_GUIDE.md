# UV Setup and Usage Guide

This guide shows how to run the COMP5241 Group 10 Learning Management System using `uv` instead of `requirements.txt`.

## Prerequisites

1. **Install uv** (if not already installed):
   ```bash
   # On macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Or using pip
   pip install uv
   
   # Or using Homebrew (macOS)
   brew install uv
   ```

2. **Install MongoDB**:
   ```bash
   # On macOS with Homebrew
   brew install mongodb-community@8.2
   
   # Start MongoDB service
   brew services start mongodb-community@8.2
   ```

## Quick Start with UV

### 1. Install Dependencies
```bash
# From the project root directory
uv sync
```

This will:
- Create a virtual environment automatically
- Install all dependencies from `pyproject.toml`
- Install development dependencies

### 2. Run the Application

#### Option A: Using the startup script (Recommended)
```bash
# From the project root directory
python start_system.py
```

This script will:
- Start MongoDB if not running
- Start the Flask backend server using `uv run`
- Open your browser to the login page

#### Option B: Manual startup
```bash
# Start MongoDB (if not already running)
brew services start mongodb-community@8.2

# Start the backend server
cd backend
uv run python app.py
```

### 3. Access the Application
- **Backend API**: http://localhost:5000/api
- **Frontend**: http://localhost:5000
- **Login Page**: http://localhost:5000/login.html

## Development Commands

### Install Dependencies
```bash
# Install all dependencies (production + development)
uv sync

# Install only production dependencies
uv sync --no-dev

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name
```

### Run Commands
```bash
# Run Python scripts
uv run python script.py

# Run tests
uv run pytest

# Run the Flask app
uv run python backend/app.py

# Run with specific Python version
uv run --python 3.11 python backend/app.py
```

### Environment Management
```bash
# Show current environment info
uv python list

# Create a new virtual environment
uv venv

# Activate the virtual environment (if needed)
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

## Environment Variables

Create a `.env` file in the `backend/` directory:
```bash
cd backend
cp env.example .env
```

Edit `.env` with your configuration:
```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
MONGODB_URI=mongodb://localhost:27017/lms_db
OPENAI_API_KEY=your-openai-api-key-here
```

## Testing

```bash
# Run all tests
uv run pytest backend/tests/ -v

# Run specific test file
uv run pytest backend/tests/test_courses.py -v

# Run tests with coverage
uv run pytest backend/tests/ --cov=backend/app
```

## Demo Users

The system comes with pre-configured demo users:

**Teachers:**
- Username: `teacher1`, Password: `password123`
- Username: `teacher2`, Password: `password123`

**Students:**
- Username: `student1`, Password: `password123`
- Username: `student2`, Password: `password123`
- Username: `student3`, Password: `password123`

## Troubleshooting

### Common Issues

1. **"uv: command not found"**
   ```bash
   # Install uv first
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **MongoDB connection issues**
   ```bash
   # Check if MongoDB is running
   brew services list | grep mongodb
   
   # Start MongoDB
   brew services start mongodb-community@8.2
   ```

3. **Port 5000 already in use**
   ```bash
   # Find and kill process using port 5000
   lsof -ti:5000 | xargs kill -9
   ```

4. **Permission issues**
   ```bash
   # Make sure you have write permissions
   chmod +x start_system.py
   ```

### Performance Benefits of UV

- **Faster dependency resolution**: UV is significantly faster than pip
- **Better dependency management**: More reliable dependency resolution
- **Automatic virtual environment**: No need to manually create/activate venvs
- **Lock file support**: Ensures reproducible builds
- **Parallel downloads**: Downloads packages in parallel for faster installation

## Migration from requirements.txt

The project has been migrated from `requirements.txt` to `pyproject.toml`. The old `requirements.txt` file is still present for reference but is no longer used.

Key changes:
- Dependencies are now defined in `pyproject.toml`
- Use `uv sync` instead of `pip install -r requirements.txt`
- Use `uv run` instead of `python` for running scripts
- Development dependencies are separated using `[project.optional-dependencies]`
