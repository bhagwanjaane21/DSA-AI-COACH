"""
AI DSA Coach — Backend API Server
Main entry point. Registers all routers and starts the uvicorn server.

Run with:
    uvicorn main:app --port 8001 --reload
    
Swagger docs available at:
    http://localhost:8001/docs
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables before importing routers
load_dotenv(override=True)

from routers import auth, schedules, submissions, revision, analytics

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI DSA Coach — Backend API",
    description=(
        "Core backend server for the AI DSA Coach application. "
        "Manages users, schedules, code submissions, SM-2 spaced repetition, "
        "revision queues, and analytics dashboards. "
        "Connects to the AI microservice (port 8000) for Gemini-powered intelligence."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS Middleware — allows frontend to communicate with backend
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Register Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router)          # POST /auth/register, POST /auth/login
app.include_router(schedules.router)     # POST /save-schedule, GET /today-tasks
app.include_router(submissions.router)   # POST /submit-code
app.include_router(revision.router)      # GET /revision-queue, PATCH /revision-queue/{id}/complete
app.include_router(analytics.router)     # GET /analytics

# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------

@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint to verify the backend is running."""
    ai_url = os.getenv("AI_SERVICE_URL", "not configured")
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_status = "configured" if supabase_url and "supabase" in supabase_url else "NOT CONFIGURED"

    return {
        "status": "ok",
        "service": "AI DSA Coach — Backend API",
        "version": "1.0.0",
        "ai_microservice": ai_url,
        "supabase": supabase_status,
        "docs": "/docs",
    }


# ---------------------------------------------------------------------------
# Run with: python main.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", "8001"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
