# 🧠 AI DSA Coach — Backend API

The core backend server for the AI DSA Coach application.  
Built with **FastAPI** + **Supabase PostgreSQL** + **SM-2 Spaced Repetition**.

---

## 🚀 How to Run the Backend

### Prerequisites
- Python 3.10+ installed
- A Supabase project (free at [supabase.com](https://supabase.com))
- The AI microservice (`ai/` folder) running on port 8000

---

### Step 1: Install Dependencies

Open a terminal in the `backend/` folder and run:

```bash
pip install -r requirements.txt
```

---

### Step 2: Configure Environment Variables

Open the `.env` file and fill in your Supabase credentials:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-jwt-key-here
AI_SERVICE_URL=http://localhost:8000
BACKEND_PORT=8001
```

**How to find your Supabase keys:**
1. Go to [supabase.com/dashboard](https://supabase.com/dashboard) → Open your project
2. Click **Settings** (gear icon at the bottom of sidebar)
3. Click **API** (under Configuration)
4. Copy the **Project URL** → paste as `SUPABASE_URL`
5. Under **Project API keys**, click **Reveal** on the `service_role` (secret) key → paste as `SUPABASE_KEY`

> ⚠️ **Important:** Use the `service_role` key (the secret one), NOT the `anon` key.

---

### Step 3: Create Database Tables in Supabase

1. Go to your **Supabase Dashboard**
2. Click **SQL Editor** in the left sidebar
3. Click **New Query**
4. Copy the entire contents of `schema.sql` and paste it into the editor
5. Click **Run** ▶️
6. You should see "Success. No rows returned" — all 6 tables and 20 seed problems are now created!

---

### Step 4: Start the AI Microservice (Port 8000)

Open **Terminal 1** and run:

```bash
cd ai
python -m uvicorn main:app --port 8000 --reload
```

Wait until you see: `Application startup complete.`

---

### Step 5: Start the Backend Server (Port 8001)

Open **Terminal 2** and run:

```bash
cd backend
python -m uvicorn main:app --port 8001 --reload
```

Wait until you see: `Application startup complete.`

---

### Step 6: Open API Documentation

Visit **[http://localhost:8001/docs](http://localhost:8001/docs)** in your browser.

You will see the interactive Swagger UI with all endpoints ready to test!

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and get JWT token |
| `POST` | `/save-schedule` | Generate AI-powered study roadmap |
| `GET` | `/today-tasks?user_id=xxx` | Get today's study tasks |
| `POST` | `/submit-code` | Submit code for AI review + SM-2 scheduling |
| `GET` | `/revision-queue?user_id=xxx` | Get pending revision problems |
| `PATCH` | `/revision-queue/{id}/complete` | Mark a revision as completed |
| `GET` | `/analytics?user_id=xxx` | Get full analytics dashboard |
| `GET` | `/` | Health check |

---

## 🏗️ Architecture

```
Frontend (React)  ←→  Backend (FastAPI :8001)  ←→  Supabase PostgreSQL
                              ↕
                    AI Layer (FastAPI :8000)  ←→  Google Gemini
```

**How a code submission flows:**
1. User submits code on the frontend
2. Frontend calls `POST /submit-code` on this backend
3. Backend fetches problem metadata from Supabase
4. Backend forwards the code to the AI microservice (`POST /api/review-code`)
5. AI layer sends it to Google Gemini and returns structured scores
6. Backend stores the submission + scores + feedback in Supabase
7. Backend runs SM-2 algorithm to schedule the next revision date
8. Backend updates the user's weak topics and learning insights
9. Backend returns the full review to the frontend

---

## 📁 Directory Structure

```
backend/
├── main.py               # App entry point — registers all routers
├── config.py             # Environment config loader
├── database.py           # Supabase client singleton
├── models.py             # Pydantic request/response schemas
├── schema.sql            # Database tables, indexes, and seed data
├── .env                  # Environment variables (not committed)
├── requirements.txt      # Python dependencies
├── test_dev_b.py         # Unit tests for SM-2 and models
├── routers/
│   ├── auth.py           # Registration & login (Supabase Auth)
│   ├── schedules.py      # Roadmap generation & daily tasks
│   ├── submissions.py    # Code submission + AI review pipeline
│   ├── revision.py       # SM-2 spaced repetition queue
│   └── analytics.py      # Dashboard data aggregation
└── services/
    ├── ai_client.py      # Async HTTP client for AI microservice
    └── sm2.py            # SM-2 spaced repetition algorithm
```

---

## 🧪 Running Tests

```bash
cd backend
$env:PYTHONIOENCODING='utf-8'; python test_dev_b.py
```

Expected output: `🎉 All tests passed! (31/31)`

---

## 🛠️ Tech Stack

| Technology | Role |
|------------|------|
| FastAPI | Web framework (async, auto-docs) |
| Supabase | Cloud PostgreSQL + Auth |
| HTTPX | Async HTTP client for AI calls |
| Pydantic | Data validation |
| SM-2 Algorithm | Spaced repetition scheduling |
| Uvicorn | ASGI web server |
