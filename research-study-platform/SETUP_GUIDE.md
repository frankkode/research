# Research Study Platform - Setup Guide

This guide provides step-by-step instructions for setting up and running the research study platform locally.

## 📋 Prerequisites

- **Python 3.9+** (for Django backend)
- **Node.js 16+** (for React frontend)
- **Git** (for version control)

## 🚀 Quick Start

### Backend Setup (Django)

1. **Navigate to backend directory**
   ```bash
   cd research-study-platform/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Test registration system**
   ```bash
   python test_registration.py
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup (React)

1. **Navigate to frontend directory**
   ```bash
   cd research-study-platform/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

## 🌐 Access Points

- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

## 📖 API Documentation

### Authentication Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/api/auth/register/` | POST | User registration | No |
| `/api/auth/login/` | POST | User login | No |
| `/api/auth/logout/` | POST | User logout | Yes |
| `/api/auth/profile/` | GET | User profile | Yes |

### Study Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/api/studies/sessions/` | GET/POST | Study sessions | Yes |
| `/api/studies/sessions/{id}/` | GET/PUT/DELETE | Specific session | Yes |

### Chat Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/api/chats/interactions/` | GET/POST | Chat interactions | Yes |
| `/api/chats/sessions/` | GET/POST | Chat sessions | Yes |

### PDF Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/api/pdfs/documents/` | GET | Available PDFs | Yes |
| `/api/pdfs/log-interaction/` | POST | Log PDF interaction | Yes |
| `/api/pdfs/session/{id}/` | GET | PDF session info | Yes |

### Quiz Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/api/quizzes/{id}/` | GET | Quiz details | Yes |
| `/api/quizzes/attempts/` | GET/POST | Quiz attempts | Yes |

### Research Endpoints

| Endpoint | Method | Description | Auth Required |
|----------|---------|-------------|---------------|
| `/api/research/studies/` | GET/POST | Research studies | Yes |
| `/api/research/participants/` | GET/POST | Participants | Yes |
| `/api/research/export/` | POST | Data export | Yes |

## 🧪 Testing

### Backend Tests

```bash
# Run Django tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report

# Run specific test file
python manage.py test apps.research.tests.test_models
```

### Frontend Tests

```bash
# Run React tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in CI mode
npm run test:ci
```

## 🔧 Development Tools

### Code Formatting

```bash
# Backend (Python)
black .
isort .
flake8 .

# Frontend (JavaScript/TypeScript)
npm run format
npm run lint
```

### Database Operations

```bash
# Create new migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset database
rm db.sqlite3
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 🐳 Docker Setup (Optional)

### Backend Docker

```dockerfile
# Dockerfile for backend
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

### Frontend Docker

```dockerfile
# Dockerfile for frontend
FROM node:16-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    depends_on:
      - db

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: research_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## 🔒 Environment Variables

Create a `.env` file in the backend directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=research_platform
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379
```

## 📁 Project Structure

```
research-study-platform/
├── backend/                 # Django backend
│   ├── apps/               # Django applications
│   │   ├── core/          # Core models and utilities
│   │   ├── authentication/ # User authentication
│   │   ├── studies/       # Study management
│   │   ├── chats/         # Chat interactions
│   │   ├── pdfs/          # PDF handling
│   │   ├── quizzes/       # Quiz system
│   │   └── research/      # Research data management
│   ├── research_platform/ # Django project settings
│   ├── requirements.txt   # Python dependencies
│   └── manage.py         # Django management script
├── frontend/              # React frontend
│   ├── src/              # Source code
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Utility functions
│   ├── package.json      # Node.js dependencies
│   └── public/           # Static assets
└── README.md            # Project documentation
```

## 🔍 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Find process using port
   lsof -i :8000
   
   # Kill process
   kill -9 <PID>
   ```

2. **Database migration errors**
   ```bash
   # Reset migrations
   rm -rf apps/*/migrations/
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Node module issues**
   ```bash
   # Clear npm cache
   npm cache clean --force
   
   # Delete node_modules and reinstall
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Python dependency issues**
   ```bash
   # Upgrade pip
   pip install --upgrade pip
   
   # Reinstall requirements
   pip install -r requirements.txt --force-reinstall
   ```

### Database Issues

1. **SQLite locked**
   ```bash
   # Close all connections and restart
   rm db.sqlite3
   python manage.py migrate
   ```

2. **Missing migrations**
   ```bash
   # Create missing migrations
   python manage.py makemigrations --empty appname
   ```

### Frontend Issues

1. **React build errors**
   ```bash
   # Clear build cache
   npm run build -- --reset-cache
   ```

2. **TypeScript errors**
   ```bash
   # Check TypeScript configuration
   npx tsc --noEmit
   ```

## 🚦 Health Checks

### Backend Health

```bash
# Check Django installation
python -c "import django; print(django.get_version())"

# Check database connection
python manage.py dbshell

# Check API endpoints
curl http://localhost:8000/api/auth/profile/
```

### Frontend Health

```bash
# Check React build
npm run build

# Check for linting errors
npm run lint

# Check for TypeScript errors
npm run type-check
```

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Material-UI Components](https://mui.com/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

---

For additional help or questions, please refer to the project documentation or contact the development team.