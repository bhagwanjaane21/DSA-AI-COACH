"""
AI Microservice HTTP Client.
Handles all communication between the backend and the AI layer (ai/ directory).

This client maps exactly to the AI layer's endpoints defined in ai/main.py:
  - POST /api/roadmap           -> generate_roadmap()
  - POST /api/review-code       -> review_code()
  - POST /api/recommend-revision -> recommend_revision()
  - POST /api/adjust-workload   -> adjust_workload()
"""
import httpx
from typing import Dict, Any, List, Optional

from config import AI_SERVICE_URL

# Timeout configuration: AI calls to Gemini can take a few seconds
_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


async def _post_to_ai(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generic async POST helper to the AI microservice.
    Raises HTTPException-compatible errors on failure.
    """
    url = f"{AI_SERVICE_URL}{endpoint}"
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


# ---------------------------------------------------------------------------
# AI Endpoint Wrappers
# Each function matches the request schema defined in ai/schemas.py exactly.
# ---------------------------------------------------------------------------

async def ai_generate_roadmap(
    user_id: str,
    classes_schedule: str,
    free_hours: int,
    weak_topics: List[str],
    current_level: str
) -> Dict[str, Any]:
    """
    Calls POST /api/roadmap on the AI microservice.
    
    Maps to ai/schemas.py -> ScheduleRequest:
        user_id, classes_schedule, free_hours, weak_topics, current_level
    
    Returns ai/schemas.py -> RoadmapResponse:
        { weekly_plan: [...], overall_focus: str }
    """
    payload = {
        "user_id": user_id,
        "classes_schedule": classes_schedule,
        "free_hours": free_hours,
        "weak_topics": weak_topics,
        "current_level": current_level,
    }
    return await _post_to_ai("/api/roadmap", payload)


async def ai_review_code(
    user_id: str,
    code: str,
    problem_description: str,
    language: str
) -> Dict[str, Any]:
    """
    Calls POST /api/review-code on the AI microservice.
    
    Maps to ai/schemas.py -> CodeReviewRequest:
        user_id, code, problem_description, language
    
    Returns ai/schemas.py -> CodeReviewResponse:
        {
            optimization_score: float,
            edge_case_score: float,
            pattern_understanding_score: float,
            weak_topic: str | null,
            feedback: str,
            time_complexity: str,
            space_complexity: str
        }
    """
    payload = {
        "user_id": user_id,
        "code": code,
        "problem_description": problem_description,
        "language": language,
    }
    return await _post_to_ai("/api/review-code", payload)


async def ai_recommend_revision(
    user_id: str,
    weak_topics: List[str],
    past_problems_solved: List[str]
) -> Dict[str, Any]:
    """
    Calls POST /api/recommend-revision on the AI microservice.
    
    Maps to ai/schemas.py -> RevisionRequest:
        user_id, weak_topics, past_problems_solved
    
    Returns ai/schemas.py -> RevisionRecommendation:
        {
            recommended_topic: str,
            underlying_pattern: str,
            problem_suggestion: str,
            reasoning: str
        }
    """
    payload = {
        "user_id": user_id,
        "weak_topics": weak_topics,
        "past_problems_solved": past_problems_solved,
    }
    return await _post_to_ai("/api/recommend-revision", payload)


async def ai_adjust_workload(
    user_id: str,
    current_plan: str,
    new_constraints: str
) -> Dict[str, Any]:
    """
    Calls POST /api/adjust-workload on the AI microservice.
    
    Maps to ai/schemas.py -> WorkloadRequest:
        user_id, current_plan, new_constraints
    
    Returns ai/schemas.py -> WorkloadResponse:
        { adjusted_plan: [...], adjustment_reasoning: str }
    """
    payload = {
        "user_id": user_id,
        "current_plan": current_plan,
        "new_constraints": new_constraints,
    }
    return await _post_to_ai("/api/adjust-workload", payload)
