# Research Study Platform

A comprehensive Django + React platform for conducting academic research studies with ChatGPT integration, PDF viewing, and quiz functionality.

## Features

- **User Authentication**: JWT-based authentication with user groups
- **Study Management**: Create and manage research studies with multiple phases
- **ChatGPT Integration**: OpenAI API integration for chatbot interactions
- **PDF Viewing**: React-PDF integration for document viewing
- **Quiz System**: Timed quizzes with multiple question types
- **Data Logging**: Comprehensive logging for research analysis
- **Group Management**: Support for different study groups (ChatGPT, PDF, Control)

## Technology Stack

### Backend
- **Django 4.2.7** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database
- **OpenAI API** - ChatGPT integration
- **Celery + Redis** - Background tasks
- **JWT Authentication** - Secure authentication

### Frontend
- **React 18** - Frontend framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **React Hook Form** - Form management
- **React PDF** - PDF viewing

## Project Structure

```
research-study-platform/
├── backend/
│   ├── research_platform/          # Django project settings
│   ├── apps/
│   │   ├── core/                   # Core models and utilities
│   │   ├── authentication/         # User authentication
│   │   ├── studies/               # Study management
│   │   ├── chats/                 # ChatGPT integration
│   │   └── quizzes/               # Quiz system
│   ├── static/                    # Static files
│   ├── media/                     # Media files
│   └── logs/                      # Log files
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── pages/                 # Page components
│   │   ├── services/              # API services
│   │   ├── types/                 # TypeScript types
│   │   ├── contexts/              # React contexts
│   │   └── utils/                 # Utility functions
│   └── public/                    # Public assets
└── docs/                          # Documentation
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis (for background tasks)

### Backend Setup

1. **Create Virtual Environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Database Setup**
   ```bash
   # Create PostgreSQL database
   createdb research_platform
   
   # Copy environment file
   cp .env.example .env
   
   # Edit .env with your settings
   ```

4. **Run Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start Development Server**
   ```bash
   npm start
   ```

### Environment Variables

Create a `.env` file in the backend directory with the following variables:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=research_platform
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379
```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - Get user profile

### Studies
- `GET /api/studies/active/` - Get active studies
- `POST /api/studies/join/{id}/` - Join a study
- `GET /api/studies/my-sessions/` - Get user's study sessions
- `POST /api/studies/log-event/` - Log study events

### Chats
- `POST /api/chats/start/` - Start new conversation
- `GET /api/chats/{id}/` - Get conversation
- `POST /api/chats/{id}/send/` - Send message
- `GET /api/chats/my-conversations/` - Get user's conversations

### Quizzes
- `GET /api/quizzes/{id}/` - Get quiz
- `POST /api/quizzes/{id}/start/` - Start quiz attempt
- `POST /api/quizzes/attempt/{id}/answer/` - Submit answer
- `POST /api/quizzes/attempt/{id}/submit/` - Submit quiz

## Database Models

### Core Models
- **User**: Extended Django user with participant info
- **UserProfile**: Additional user information

### Study Models
- **Study**: Research study configuration
- **StudySession**: Individual user study sessions
- **StudyLog**: Event logging for analysis

### Chat Models
- **ChatConversation**: Chat conversation container
- **ChatMessage**: Individual chat messages
- **ChatAnalytics**: Conversation analytics

### Quiz Models
- **Quiz**: Quiz configuration
- **Question**: Quiz questions
- **QuestionChoice**: Multiple choice options
- **QuizAttempt**: User quiz attempts
- **QuizAnswer**: Individual question answers

## Development Commands

### Backend
```bash
# Run tests
python manage.py test

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Run development server
python manage.py runserver
```

### Frontend
```bash
# Start development server
npm start

# Build for production
npm run build

# Run tests
npm test

# Type check
npx tsc --noEmit
```

## Production Deployment

1. **Environment Setup**
   - Set `DEBUG=False` in production
   - Configure proper `ALLOWED_HOSTS`
   - Use environment variables for sensitive data

2. **Database**
   - Use PostgreSQL in production
   - Configure connection pooling
   - Set up database backups

3. **Static Files**
   - Configure WhiteNoise for static files
   - Use CDN for media files

4. **Security**
   - Configure HTTPS
   - Set up proper CORS headers
   - Use secure session cookies

## Research Ethics

This platform is designed for academic research. Please ensure:
- Proper IRB approval for your studies
- Informed consent from participants
- Data privacy compliance
- Secure data storage and transmission

## License

This project is licensed under the MIT License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed information