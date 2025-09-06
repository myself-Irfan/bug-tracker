# 🐛 BugTracker

BugTracker is a simple bug tracking and project collaboration system built with Django and Django REST Framework. It includes real-time updates via Django Channels and Redis.

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/bugtracker.git
cd bugtracker
```

### 2. Create a `.env` file

```ini
SECRET_KEY=your-secret-key
DB_NAME=bugtracker
DB_USER=postgres
DB_PWD=12345
DB_HOST=localhost
DB_PORT=5432
DB_SCHEMA=public

ACCESS_TOKEN_LIFETIME_IN_MIN=60
REFRESH_TOKEN_LIFETIME_IN_DAYS=7
```

### 3. Build and run with Docker Compose

```bash
docker-compose up --build
```

> **Note:** Redis and Channels are configured inside Docker. Redis is used for message passing between consumers and Django via Channels.

---

## 🌐 API Endpoints (Highlights)

### ✨ Authentication

* `POST /api/token/` - Get access and refresh token
* `POST /api/token/refresh/` - Refresh token

### 📆 Projects

* `GET /api/projects/` - List user-accessible projects (paginated)
* `POST /api/projects/` - Create new project

### 🛠️ Bugs

* `GET /api/bugs/` - List bugs
* `POST /api/bugs/` - Create bug
* `GET /api/bugs/{id}/comments/` - Comments on a bug

### 🔹 Activities

* `GET /api/v1/activity/` - List filtered activities
* `GET /api/v1/activity/{id}` - Activity detail

### 📊 Dashboard

* `GET /api/v1/dashboard-stats/` - Summary stats

### 📖 API Docs

* Swagger: `GET /swagger/`
* Redoc: `GET /redoc/`

---

## 🌌 Real-Time WebSocket Setup & Testing

### Django Channels + Redis

* Configured with `channels` and `channels_redis`
* Redis must be running (handled in Docker)

### ASGI Setup

Ensure this is set in `settings.py`:

```python
ASGI_APPLICATION = 'bugtracker.asgi.application'
CHANNEL_LAYERS = {
  'default': {
    'BACKEND': 'channels_redis.core.RedisChannelLayer',
    'CONFIG': {
      'hosts': [('127.0.0.1', 6379)],
    },
  },
}
```

### Starting WebSocket Server

When using Docker:

```bash
docker-compose up
```

Django runs with `gunicorn` using `uvicorn.workers.UvicornWorker` (ASGI-compatible).

### Example Consumer Test

Assuming you have a WebSocket URL `ws://localhost:8000/ws/activity/`

```bash
# Requires websocat: https://github.com/vi/websocat
websocat ws://localhost:8000/ws/activity/
```

You should receive live activity logs as they happen.

---

## 🔧 Development Tips

* Use DRF's built-in pagination via `SetPagination`
* Use SlugRelatedField to handle relations by `username`
* Logging and audit trails handled via `ActivityLog`

---

## 💡 Testing Auth

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

Use the returned access token in your headers:

```bash
-H "Authorization: Bearer <access_token>"
```

---