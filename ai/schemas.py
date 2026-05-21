from pydantic import BaseModel
from typing import List, Optional

# --- Requests ---

class ScheduleRequest(BaseModel):
    user_id: str
    classes_schedule: str
    free_hours: int
    weak_topics: List[str]
    current_level: str

class CodeReviewRequest(BaseModel):
    user_id: str
    code: str
    problem_description: str
    language: str

class RevisionRequest(BaseModel):
    user_id: str
    weak_topics: List[str]
    past_problems_solved: List[str]

class WorkloadRequest(BaseModel):
    user_id: str
    current_plan: str
    new_constraints: str

# --- Responses (Structured JSON from LLM) ---

class RoadmapTask(BaseModel):
    day: str
    topic: str
    problems_to_solve: int
    concept_to_learn: str

class RoadmapResponse(BaseModel):
    weekly_plan: List[RoadmapTask]
    overall_focus: str

class CodeReviewResponse(BaseModel):
    optimization_score: float # 0.0 to 1.0
    edge_case_score: float # 0.0 to 1.0
    pattern_understanding_score: float # 0.0 to 1.0
    weak_topic: Optional[str] = None
    feedback: str
    time_complexity: str
    space_complexity: str

class RevisionRecommendation(BaseModel):
    recommended_topic: str
    underlying_pattern: str
    problem_suggestion: str
    reasoning: str

class WorkloadResponse(BaseModel):
    adjusted_plan: List[RoadmapTask]
    adjustment_reasoning: str
