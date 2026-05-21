import os
import json
from google import genai
from google.genai import types
from typing import Dict, Any

from schemas import (
    ScheduleRequest, RoadmapResponse,
    CodeReviewRequest, CodeReviewResponse,
    RevisionRequest, RevisionRecommendation,
    WorkloadRequest, WorkloadResponse
)
from prompts import (
    ROADMAP_SYSTEM_PROMPT,
    CODE_REVIEW_SYSTEM_PROMPT,
    REVISION_SYSTEM_PROMPT,
    WORKLOAD_SYSTEM_PROMPT
)

# Lazy-initialized client (created on first use)
_client = None

def _get_client() -> genai.Client:
    """Get or create the Gemini client using the API key from environment."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("GEMINI_API_KEY is not set correctly in .env")
        _client = genai.Client(api_key=api_key)
    return _client

def _get_gemini_response(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    client = _get_client()

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
        )
    )

    try:
        return json.loads(response.text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {response.text}")
        raise ValueError("Invalid JSON response from LLM") from e

def generate_roadmap(request: ScheduleRequest) -> RoadmapResponse:
    user_prompt = f"""
    Schedule: {request.classes_schedule}
    Free Hours per week: {request.free_hours}
    Weak Topics: {', '.join(request.weak_topics)}
    Current Level: {request.current_level}
    
    Generate a roadmap in this exact JSON schema:
    {{
      "weekly_plan": [
        {{
          "day": "Monday",
          "topic": "Arrays",
          "problems_to_solve": 2,
          "concept_to_learn": "Sliding Window"
        }}
      ],
      "overall_focus": "string"
    }}
    """
    
    data = _get_gemini_response(ROADMAP_SYSTEM_PROMPT, user_prompt)
    return RoadmapResponse(**data)

def review_code(request: CodeReviewRequest) -> CodeReviewResponse:
    user_prompt = f"""
    Problem: {request.problem_description}
    Language: {request.language}
    Code Submission:
    ```{request.language}
    {request.code}
    ```
    
    Generate a code review in this exact JSON schema:
    {{
      "optimization_score": 0.0-1.0,
      "edge_case_score": 0.0-1.0,
      "pattern_understanding_score": 0.0-1.0,
      "weak_topic": "string or null",
      "feedback": "string",
      "time_complexity": "string",
      "space_complexity": "string"
    }}
    """
    
    data = _get_gemini_response(CODE_REVIEW_SYSTEM_PROMPT, user_prompt)
    return CodeReviewResponse(**data)

def recommend_revision(request: RevisionRequest) -> RevisionRecommendation:
    user_prompt = f"""
    Weak Topics: {', '.join(request.weak_topics)}
    Past Problems Solved: {', '.join(request.past_problems_solved)}
    
    Generate a revision recommendation in this exact JSON schema:
    {{
      "recommended_topic": "string",
      "underlying_pattern": "string",
      "problem_suggestion": "string",
      "reasoning": "string"
    }}
    """
    
    data = _get_gemini_response(REVISION_SYSTEM_PROMPT, user_prompt)
    return RevisionRecommendation(**data)

def adjust_workload(request: WorkloadRequest) -> WorkloadResponse:
    user_prompt = f"""
    Current Plan: {request.current_plan}
    New Constraints / Events: {request.new_constraints}
    
    Adjust the workload and return in this exact JSON schema:
    {{
      "adjusted_plan": [
        {{
          "day": "Monday",
          "topic": "Arrays",
          "problems_to_solve": 2,
          "concept_to_learn": "Sliding Window"
        }}
      ],
      "adjustment_reasoning": "string"
    }}
    """
    
    data = _get_gemini_response(WORKLOAD_SYSTEM_PROMPT, user_prompt)
    return WorkloadResponse(**data)
