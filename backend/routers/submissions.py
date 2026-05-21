"""
Submissions Router — POST /submit-code

Handles the full code submission pipeline:
1. Fetches problem metadata from DB
2. Sends code to the AI microservice for review (ai/api/review-code)
3. Stores the structured submission with all metadata scores
4. Runs SM-2 algorithm to calculate next revision date
5. Upserts the revision_queue entry
6. Updates the user's weak_topics and learning_insights
"""
from fastapi import APIRouter, HTTPException
from datetime import date

from database import get_supabase
from models import SubmitCodeRequest, SubmissionResponse
from services.ai_client import ai_review_code
from services.sm2 import calculate_sm2, scores_to_grade

router = APIRouter(tags=["Submissions"])


@router.post("/submit-code", response_model=SubmissionResponse)
async def submit_code(request: SubmitCodeRequest):
    """
    Submit a code solution for AI review.
    
    Flow:
        1. Fetch problem metadata (title, description, topic) from the problems table
        2. Call AI microservice POST /api/review-code for structured review
        3. Save submission with all scores + metadata to submissions table
        4. Calculate SM-2 grade from review scores
        5. Upsert revision_queue with next scheduled revision date
        6. Update user's weak_topics array if a weak topic is detected
        7. Update learning_insights with improvement trend data
    """
    db = get_supabase()

    # --- Step 1: Fetch problem metadata ---
    problem_result = db.table("problems").select("*").eq(
        "id", request.problem_id
    ).execute()

    if not problem_result.data:
        raise HTTPException(
            status_code=404,
            detail=f"Problem '{request.problem_id}' not found in database."
        )

    problem = problem_result.data[0]

    # --- Step 2: Call AI microservice for code review ---
    try:
        review = await ai_review_code(
            user_id=request.user_id,
            code=request.code,
            problem_description=problem.get("description", problem.get("title", "")),
            language=request.language,
        )
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"AI microservice error: {str(e)}"
        )

    optimization_score = review.get("optimization_score", 0.0)
    edge_case_score = review.get("edge_case_score", 0.0)
    pattern_score = review.get("pattern_understanding_score", 0.0)
    weak_topic = review.get("weak_topic")
    feedback = review.get("feedback", "")
    time_complexity = review.get("time_complexity", "")
    space_complexity = review.get("space_complexity", "")

    # --- Step 3: Save submission to database ---
    submission_data = {
        "user_id": request.user_id,
        "problem_id": request.problem_id,
        "code": request.code,
        "language": request.language,
        "optimization_score": optimization_score,
        "edge_case_score": edge_case_score,
        "pattern_understanding_score": pattern_score,
        "feedback": feedback,
        "time_complexity": time_complexity,
        "space_complexity": space_complexity,
        "hints_used": request.hints_used,
        "time_taken": request.time_taken,
        "weak_topic": weak_topic,
    }

    insert_result = db.table("submissions").insert(submission_data).execute()

    if not insert_result.data:
        raise HTTPException(status_code=500, detail="Failed to save submission.")

    submission_id = insert_result.data[0]["id"]

    # --- Step 4: Calculate SM-2 grade ---
    sm2_grade = scores_to_grade(optimization_score, edge_case_score, pattern_score)

    # Check for existing revision entry for this user+problem
    existing_revision = db.table("revision_queue").select("*").eq(
        "user_id", request.user_id
    ).eq(
        "problem_id", request.problem_id
    ).execute()

    if existing_revision.data:
        # Update existing SM-2 state
        prev = existing_revision.data[0]
        sm2_result = calculate_sm2(
            grade=sm2_grade,
            repetition=prev.get("repetition", 0),
            easiness_factor=prev.get("easiness_factor", 2.5),
            interval=prev.get("interval_days", 1),
        )

        db.table("revision_queue").update({
            "scheduled_date": sm2_result.scheduled_date.isoformat(),
            "status": "Pending",
            "repetition": sm2_result.repetition,
            "easiness_factor": sm2_result.easiness_factor,
            "interval_days": sm2_result.interval_days,
            "reasoning": f"SM-2 grade {sm2_grade}/5 — {feedback[:200]}",
            "updated_at": "now()",
        }).eq("id", prev["id"]).execute()
    else:
        # Create new revision entry
        sm2_result = calculate_sm2(grade=sm2_grade)
        topic = problem.get("topic", weak_topic or "General")

        db.table("revision_queue").insert({
            "user_id": request.user_id,
            "problem_id": request.problem_id,
            "topic": topic,
            "scheduled_date": sm2_result.scheduled_date.isoformat(),
            "status": "Pending",
            "repetition": sm2_result.repetition,
            "easiness_factor": sm2_result.easiness_factor,
            "interval_days": sm2_result.interval_days,
            "reasoning": f"SM-2 grade {sm2_grade}/5 — {feedback[:200]}",
        }).execute()

    # --- Step 6: Update user's weak_topics if detected ---
    if weak_topic:
        user_result = db.table("users").select("weak_topics").eq(
            "id", request.user_id
        ).execute()

        if user_result.data:
            current_weak = user_result.data[0].get("weak_topics", []) or []
            if weak_topic not in current_weak:
                current_weak.append(weak_topic)
                db.table("users").update({
                    "weak_topics": current_weak,
                    "updated_at": "now()",
                }).eq("id", request.user_id).execute()

    # --- Step 7: Update learning_insights ---
    _update_learning_insights(
        db, request.user_id, request.problem_id,
        optimization_score, edge_case_score, pattern_score, weak_topic
    )

    return SubmissionResponse(
        submission_id=submission_id,
        problem_id=request.problem_id,
        optimization_score=optimization_score,
        edge_case_score=edge_case_score,
        pattern_understanding_score=pattern_score,
        feedback=feedback,
        time_complexity=time_complexity,
        space_complexity=space_complexity,
        weak_topic=weak_topic,
        sm2_grade=sm2_grade,
        next_revision_date=sm2_result.scheduled_date.isoformat(),
    )


def _update_learning_insights(
    db, user_id: str, problem_id: str,
    opt_score: float, edge_score: float, pattern_score: float,
    weak_topic: str | None
):
    """
    Update the learning_insights table with trend data from this submission.
    Tracks improvement over time per topic and maintains revision history.
    """
    existing = db.table("learning_insights").select("*").eq(
        "user_id", user_id
    ).execute()

    avg_score = round((opt_score + edge_score + pattern_score) / 3.0, 4)
    new_entry = {
        "problem_id": problem_id,
        "score": avg_score,
        "date": date.today().isoformat(),
    }

    if existing.data:
        insights = existing.data[0]
        trends = insights.get("improvement_trends", {}) or {}
        history = insights.get("revision_history", []) or []
        weak_topics = insights.get("weak_topics", []) or []

        # Add score to topic trend
        topic_key = weak_topic or "General"
        if topic_key not in trends:
            trends[topic_key] = []
        trends[topic_key].append(avg_score)

        # Keep last 50 entries in revision history
        history.append(new_entry)
        history = history[-50:]

        # Update weak topics
        if weak_topic and weak_topic not in weak_topics:
            weak_topics.append(weak_topic)

        db.table("learning_insights").update({
            "improvement_trends": trends,
            "revision_history": history,
            "weak_topics": weak_topics,
            "updated_at": "now()",
        }).eq("user_id", user_id).execute()
    else:
        # Create initial insights row
        trends = {}
        if weak_topic:
            trends[weak_topic] = [avg_score]

        db.table("learning_insights").insert({
            "user_id": user_id,
            "weak_topics": [weak_topic] if weak_topic else [],
            "improvement_trends": trends,
            "revision_history": [new_entry],
        }).execute()
