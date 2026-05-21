import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from schemas import (
    ScheduleRequest, RoadmapResponse,
    CodeReviewRequest, CodeReviewResponse,
    RevisionRequest, RevisionRecommendation,
    WorkloadRequest, WorkloadResponse
)
from services import (
    generate_roadmap,
    review_code,
    recommend_revision,
    adjust_workload
)

# Load environment variables from .env file
load_dotenv(override=True)

app = FastAPI(
    title="AI DSA Coach - Intelligence Layer",
    description="Microservice providing AI capabilities for the DSA Coach app",
    version="1.0.0",
)

# Allow CORS for frontend/backend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def health_check():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    key_status = "configured" if gemini_key and gemini_key != "your_gemini_api_key_here" else "MISSING"
    return {
        "status": "ok",
        "message": "AI microservice is running.",
        "gemini_api_key": key_status
    }

@app.post("/api/roadmap", response_model=RoadmapResponse)
def create_roadmap_endpoint(request: ScheduleRequest):
    try:
        return generate_roadmap(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/review-code", response_model=CodeReviewResponse)
def review_code_endpoint(request: CodeReviewRequest):
    try:
        return review_code(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend-revision", response_model=RevisionRecommendation)
def recommend_revision_endpoint(request: RevisionRequest):
    try:
        return recommend_revision(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/adjust-workload", response_model=WorkloadResponse)
def adjust_workload_endpoint(request: WorkloadRequest):
    try:
        return adjust_workload(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
