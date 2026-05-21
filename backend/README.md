# AI DSA Coach — Backend API

The core backend server for the AI DSA Coach application, built with **FastAPI** and **Supabase PostgreSQL**.

## Tech Stack
- **FastAPI** — High-performance async Python web framework
- **Supabase** — Cloud PostgreSQL database + Auth
- **HTTPX** — Async HTTP client (connects to AI microservice)
- **Pydantic** — Data validation and serialization
- **SM-2 Algorithm** — Spaced repetition scheduling for revision

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env` and fill in your Supabase credentials:
```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key
AI_SERVICE_URL=http://localhost:8000
BACKEND_PORT=8001
```

### 3. Create Database Tables
Go to your **Supabase Dashboard → SQL Editor** and run the contents of `schema.sql`.

### 4. Start the AI Microservice First
```bash
cd ../ai
uvicorn main:app --port 8000 --reload
```

### 5. Start the Backend Server
```bash
cd ../backend
uvicorn main:app --port 8001 --reload
```

### 6. Open API Documentation
Visit [http://localhost:8001/docs](http://localhost:8001/docs) for the interactive Swagger UI.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and get JWT token |
| POST | `/save-schedule` | Generate AI-powered study roadmap |
| GET | `/today-tasks` | Get today's study tasks |
| POST | `/submit-code` | Submit code for AI review + SM-2 scheduling |
| GET | `/revision-queue` | Get pending revision problems |
| PATCH | `/revision-queue/{id}/complete` | Mark a revision as completed |
| GET | `/analytics` | Get full analytics dashboard data |
| GET | `/` | Health check |

## Architecture
```
Frontend (React) ←→ Backend (FastAPI :8001) ←→ Supabase PostgreSQL
                                    ↕
                          AI Layer (FastAPI :8000) ←→ Google Gemini
```

## Directory Structure
```
backend/
├── main.py               # App entry point, registers all routers
├── config.py             # Environment config loader
├── database.py           # Supabase client singleton
├── models.py             # Pydantic request/response schemas
├── schema.sql            # Database tables, indexes, and seeds
├── routers/
│   ├── auth.py           # Registration & login
│   ├── schedules.py      # Roadmap generation & daily tasks
│   ├── submissions.py    # Code submission + AI review pipeline
│   ├── revision.py       # SM-2 spaced repetition queue
│   └── analytics.py      # Dashboard data aggregation
├── services/
│   ├── ai_client.py      # Async HTTP client for AI microservice
│   └── sm2.py            # SM-2 spaced repetition algorithm
└── test_dev_b.py         # Unit tests for SM-2 & models
```
