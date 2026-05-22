"""
Schedules Router — POST /save-schedule, GET /today-tasks

Handles schedule creation (calls AI microservice for roadmap generation)
and retrieves today's specific tasks from the saved weekly plan.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database import get_supabase
from services.ai_client import ai_generate_roadmap

router = APIRouter(tags=["Schedules"])


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class SaveScheduleRequest(BaseModel):
    """Request body for POST /save-schedule."""
    user_id: str
    classes_schedule: str
    free_hours: int
    weak_topics: List[str] = []
    current_level: str = "Beginner"


class RoadmapTask(BaseModel):
    """A single day's task in the weekly plan."""
    day: str
    topic: str
    problems_to_solve: int
    concept_to_learn: str


class SaveScheduleResponse(BaseModel):
    """Response for POST /save-schedule."""
    schedule_id: str
    user_id: str
    weekly_plan: List[RoadmapTask]
    overall_focus: str
    message: str


class TodayTask(BaseModel):
    """A task scheduled for today."""
    topic: str
    problems_to_solve: int
    concept_to_learn: str


class TodayTasksResponse(BaseModel):
    """Response for GET /today-tasks."""
    user_id: str
    today: str
    day_name: str
    tasks: List[TodayTask]
    overall_focus: str
    message: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/save-schedule", response_model=SaveScheduleResponse)
async def save_schedule(request: SaveScheduleRequest):
    """
    Generate and save a personalized study schedule.
    
    Flow:
        1. Call the AI microservice POST /api/roadmap with the user's constraints
        2. Save the generated weekly plan to the schedules table in Supabase
        3. Update the user's weak_topics and current_level profile
        4. Return the full roadmap to the frontend for visualization
    """
    db = get_supabase()

    # --- Step 1: Call AI microservice to generate roadmap ---
    try:
        ai_response = await ai_generate_roadmap(
            user_id=request.user_id,
            classes_schedule=request.classes_schedule,
            free_hours=request.free_hours,
            weak_topics=request.weak_topics,
            current_level=request.current_level,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI microservice error: {str(e)}"
        )

    weekly_plan = ai_response.get("weekly_plan", [])
    overall_focus = ai_response.get("overall_focus", "")

    # --- Step 2: Save schedule to Supabase ---
    schedule_data = {
        "user_id": request.user_id,
        "classes_schedule": request.classes_schedule,
        "free_hours": request.free_hours,
        "weekly_plan": weekly_plan,
        "overall_focus": overall_focus,
    }

    insert_result = db.table("schedules").insert(schedule_data).execute()

    if not insert_result.data:
        raise HTTPException(status_code=500, detail="Failed to save schedule.")

    schedule_id = insert_result.data[0]["id"]

    # --- Step 3: Update user profile with weak topics ---
    user_result = db.table("users").select("weak_topics").eq(
        "id", request.user_id
    ).execute()

    if user_result.data:
        existing_weak = user_result.data[0].get("weak_topics", []) or []
        merged_weak = list(set(existing_weak + request.weak_topics))

        db.table("users").update({
            "weak_topics": merged_weak,
            "current_level": request.current_level,
            "updated_at": "now()",
        }).eq("id", request.user_id).execute()

    # --- Step 4: Return the roadmap ---
    plan_models = [RoadmapTask(**task) for task in weekly_plan]

    return SaveScheduleResponse(
        schedule_id=schedule_id,
        user_id=request.user_id,
        weekly_plan=plan_models,
        overall_focus=overall_focus,
        message="Schedule generated and saved successfully!",
    )


@router.get("/today-tasks", response_model=TodayTasksResponse)
async def get_today_tasks(
    user_id: str = Query(..., description="The user's ID"),
):
    """
    Get today's study tasks from the user's most recent schedule.
    
    Flow:
        1. Fetch the user's latest saved schedule from Supabase
        2. Determine today's day name (Monday, Tuesday, etc.)
        3. Filter the weekly plan for tasks matching today's day
        4. Return the filtered tasks to the frontend
    """
    db = get_supabase()

    # --- Step 1: Fetch the latest schedule ---
    schedule_result = db.table("schedules").select("*").eq(
        "user_id", user_id
    ).order("created_at", desc=True).limit(1).execute()

    if not schedule_result.data:
        raise HTTPException(
            status_code=404,
            detail="No schedule found. Please generate a roadmap first."
        )

    schedule = schedule_result.data[0]
    weekly_plan = schedule.get("weekly_plan", [])
    overall_focus = schedule.get("overall_focus", "")

    # --- Step 2: Determine today's day ---
    today = datetime.now()
    day_name = today.strftime("%A")  # e.g., "Monday", "Tuesday"

    # --- Step 3: Filter tasks for today ---
    today_tasks = []
    for task in weekly_plan:
        task_day = task.get("day", "").strip().lower()
        if task_day == day_name.lower():
            today_tasks.append(TodayTask(
                topic=task.get("topic", ""),
                problems_to_solve=task.get("problems_to_solve", 0),
                concept_to_learn=task.get("concept_to_learn", ""),
            ))

    # --- Step 4: Build response ---
    if today_tasks:
        message = f"You have {len(today_tasks)} task(s) for today. Let's go!"
    else:
        message = f"No tasks scheduled for {day_name}. Enjoy your rest day, or practice revision!"

    return TodayTasksResponse(
        user_id=user_id,
        today=today.strftime("%Y-%m-%d"),
        day_name=day_name,
        tasks=today_tasks,
        overall_focus=overall_focus,
        message=message,
    )
