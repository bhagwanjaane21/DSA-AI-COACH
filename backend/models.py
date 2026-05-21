"""
Pydantic models for Dev B endpoints: Submissions, Revision Queue, Analytics.
These schemas define the request/response contracts for the backend API.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime


# ---------------------------------------------------------------------------
# Submission Models
# ---------------------------------------------------------------------------

class SubmitCodeRequest(BaseModel):
    """Request body for POST /submit-code."""
    user_id: str
    problem_id: str
    code: str
    language: str = "python"
    hints_used: int = Field(default=0, ge=0)
    time_taken: int = Field(default=0, ge=0, description="Time taken in seconds")


class SubmissionResponse(BaseModel):
    """Response for POST /submit-code — includes AI review + SM-2 scheduling."""
    submission_id: str
    problem_id: str
    optimization_score: float
    edge_case_score: float
    pattern_understanding_score: float
    feedback: str
    time_complexity: str
    space_complexity: str
    weak_topic: Optional[str] = None
    sm2_grade: int = Field(description="SM-2 quality grade (0-5)")
    next_revision_date: Optional[str] = Field(
        default=None,
        description="Next scheduled revision date (YYYY-MM-DD)"
    )


# ---------------------------------------------------------------------------
# Revision Queue Models
# ---------------------------------------------------------------------------

class RevisionItem(BaseModel):
    """A single item in the revision queue."""
    id: str
    problem_id: str
    topic: str
    scheduled_date: str
    status: str
    reasoning: Optional[str] = None
    repetition: int = 0
    easiness_factor: float = 2.5
    interval_days: int = 1


class RevisionQueueResponse(BaseModel):
    """Response for GET /revision-queue."""
    user_id: str
    total_pending: int
    due_today: int
    revision_items: List[RevisionItem]


# ---------------------------------------------------------------------------
# Analytics Models
# ---------------------------------------------------------------------------

class TopicMetric(BaseModel):
    """Aggregated score metrics for a single topic."""
    topic: str
    total_submissions: int
    avg_optimization_score: float
    avg_edge_case_score: float
    avg_pattern_score: float
    avg_overall_score: float


class RecentSubmission(BaseModel):
    """Summary of a recent submission for the analytics dashboard."""
    submission_id: str
    problem_id: str
    language: str
    optimization_score: float
    edge_case_score: float
    pattern_understanding_score: float
    weak_topic: Optional[str] = None
    created_at: str


class AnalyticsResponse(BaseModel):
    """Response for GET /analytics — full dashboard data."""
    user_id: str
    total_submissions: int
    total_problems_solved: int
    weak_topics: List[str]
    topic_breakdown: List[TopicMetric]
    recent_submissions: List[RecentSubmission]
    pending_revisions: int
    current_level: str
    improvement_trends: dict = Field(
        default_factory=dict,
        description="Topic -> list of scores over time"
    )
