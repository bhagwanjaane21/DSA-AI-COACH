"""
Revision Queue Router — GET /revision-queue

Retrieves the user's pending revision items, sorted by scheduled date.
Supports filtering by status and highlights problems due today.
"""
from fastapi import APIRouter, HTTPException, Query
from datetime import date

from database import get_supabase
from models import RevisionQueueResponse, RevisionItem

router = APIRouter(tags=["Revision"])


@router.get("/revision-queue", response_model=RevisionQueueResponse)
async def get_revision_queue(
    user_id: str = Query(..., description="The user's ID"),
    status: str = Query("Pending", description="Filter by status: Pending, Completed, or All"),
):
    """
    Get the revision queue for a user.
    
    Returns all pending revision items sorted by scheduled_date (earliest first).
    Includes SM-2 state (repetition count, easiness factor, interval) for each item.
    """
    db = get_supabase()

    # Build query
    query = db.table("revision_queue").select("*").eq("user_id", user_id)

    if status != "All":
        query = query.eq("status", status)

    query = query.order("scheduled_date", desc=False)
    result = query.execute()

    if not result.data:
        return RevisionQueueResponse(
            user_id=user_id,
            total_pending=0,
            due_today=0,
            revision_items=[],
        )

    today = date.today().isoformat()
    items = []
    due_today_count = 0

    for row in result.data:
        scheduled = row.get("scheduled_date", "")
        if scheduled <= today and row.get("status") == "Pending":
            due_today_count += 1

        items.append(RevisionItem(
            id=row["id"],
            problem_id=row["problem_id"],
            topic=row.get("topic", ""),
            scheduled_date=scheduled,
            status=row.get("status", "Pending"),
            reasoning=row.get("reasoning"),
            repetition=row.get("repetition", 0),
            easiness_factor=row.get("easiness_factor", 2.5),
            interval_days=row.get("interval_days", 1),
        ))

    total_pending = sum(1 for item in items if item.status == "Pending")

    return RevisionQueueResponse(
        user_id=user_id,
        total_pending=total_pending,
        due_today=due_today_count,
        revision_items=items,
    )


@router.patch("/revision-queue/{revision_id}/complete")
async def mark_revision_complete(revision_id: str):
    """
    Mark a revision item as completed.
    Called when the user re-solves a revision problem.
    """
    db = get_supabase()

    result = db.table("revision_queue").update({
        "status": "Completed",
        "updated_at": "now()",
    }).eq("id", revision_id).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Revision item not found.")

    return {"message": "Revision marked as completed.", "id": revision_id}
