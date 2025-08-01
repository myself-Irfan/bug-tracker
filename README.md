```markdown
# Bug Tracker Application

A Django-based bug tracking system with real-time WebSocket notifications.

## Features

- JWT Authentication
- CRUD operations for Projects, Bugs, and Comments
- Real-time notifications via WebSockets
- Activity logging
- Typing indicators
- Swagger API documentation
- User assignment and filtering

## Setup Instructions

### Prerequisites
- Python 3.8+
- Redis server
- Virtual environment (recommended)

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Start Redis server:
```bash
redis-server
```

4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Authentication
- POST `/api/token/` - Get JWT token
- POST `/api/token/refresh/` - Refresh JWT token

### Projects
- GET `/api/projects/` - List projects
- POST `/api/projects/` - Create project
- GET `/api/projects/{id}/` - Get project details
- PUT `/api/projects/{id}/` - Update project
- DELETE `/api/projects/{id}/` - Delete project

### Bugs
- GET `/api/bugs/` - List bugs (supports filtering by status, project, priority)
- POST `/api/bugs/` - Create bug
- GET `/api/bugs/{id}/` - Get bug details
- PUT `/api/bugs/{id}/` - Update bug
- DELETE `/api/bugs/{id}/` - Delete bug
- GET `/api/bugs/assigned/` - Get bugs assigned to current user

### Comments
- GET `/api/bugs/{bug_id}/comments/` - List comments for a bug
- POST `/api/bugs/{bug_id}/comments/` - Create comment

### Activity Log
- GET `/api/projects/{project_id}/activity/` - Get project activity log

## WebSocket Usage

Connect to: `ws://localhost:8000/ws/project/{project_id}/`

### Events Received:
- `bug_notification` - When bugs are created/updated
- `comment_notification` - When comments are added
- `typing_indicator` - When users are typing
- `activity_log` - Activity updates

### Events to Send:
```json
{
    "type": "typing_indicator",
    "bug_id": 1,
    "is_typing": true
}
```

## Testing WebSocket Events

1. Open browser console
2. Connect to WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/project/1/');
ws.onmessage = function(event) {
    console.log('Message:', JSON.parse(event.data));
};
```

3. Create/update bugs or add comments via API to see real-time updates

## API Documentation

- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Authentication

Include JWT token in headers:
```
Authorization: Bearer <your_jwt_token>
```
```

This complete implementation includes all the requirements from the test:

**Features Implemented:**
✅ Django REST Framework with JWT authentication
✅ Models: Project, Bug, Comment, ActivityLog
✅ CRUD APIs for all models
✅ WebSocket real-time notifications
✅ Redis channel layer integration
✅ Filtering and search capabilities
✅ Activity logging with WebSocket streaming
✅ Typing indicators (bonus)
✅ Swagger/OpenAPI documentation (bonus)

**Key Technical Points:**
- Uses Django Channels for WebSocket support
- JWT token authentication for API security
- Redis as the channel layer backend
- Real-time notifications for bug updates and comments
- Permission-based WebSocket rooms (project-based)
- Activity logging for audit trail
- Clean, modular code structure following Django best practices

The application is ready to run and demonstrates full-stack Django development with modern real-time features. All endpoints are documented and the WebSocket functionality provides live updates across connected clients.