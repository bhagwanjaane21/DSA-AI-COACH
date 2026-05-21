"""
Analytics Router — GET /analytics

Aggregates the user's full submission history, topic-level performance,
weak topic tracking, improvement trends, and revision stats into a single
dashboard payload.
"""
from fastapi import APIRouter, HTTPException, Query
from collections import defaultdict

from database import get_supabase
from models import AnalyticsResponse, TopicMetric, RecentSubmission

router = APIRouter(tags=["Analytics"])


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    user_id: str = Query(..., description="The user's ID"),
):
    """
    Get comprehensive analytics for a user.
    
    Aggregates:
        - Total submissions and unique problems solved
        - Per-topic score averages (optimization, edge case, pattern)
        - Recent submission history (last 20)
        - Pending revision count
        - Improvement trends over time from learning_insights
        - Current weak topics
    """
    db = get_supabase()

    # --- Fetch user profile ---
    user_result = db.table("users").select("*").eq("id", user_id).execute()
    if not user_result.data:
        raise HTTPException(status_code=404, detail="User not found.")

    user = user_result.data[0]
    current_level = user.get("current_level", "Beginner")
    user_weak_topics = user.get("weak_topics", []) or []

    # --- Fetch all submissions ---
    submissions_result = db.table("submissions").select("*").eq(
        "user_id", user_id
    ).order("created_at", desc=True).execute()

    submissions = submissions_result.data or []
    total_submissions = len(submissions)
    unique_problems = set(s["problem_id"] for s in submissions)
    total_problems_solved = len(unique_problems)

    # --- Topic breakdown ---
    topic_data = defaultdict(lambda: {
        "opt_scores": [],
        "edge_scores": [],
        "pattern_scores": [],
    })

    # We need problem metadata to group by topic
    if submissions:
        problem_ids = list(unique_problems)
        problems_result = db.table("problems").select("id, topic").in_(
            "id", problem_ids
        ).execute()
        problem_topic_map = {
            p["id"]: p.get("topic", "Unknown")
            for p in (problems_result.data or [])
        }
    else:
        problem_topic_map = {}

    for s in submissions:
        topic = problem_topic_map.get(s["problem_id"], s.get("weak_topic", "Unknown"))
        topic_data[topic]["opt_scores"].append(s.get("optimization_score", 0))
        topic_data[topic]["edge_scores"].append(s.get("edge_case_score", 0))
        topic_data[topic]["pattern_scores"].append(s.get("pattern_understanding_score", 0))

    topic_breakdown = []
    for topic, data in topic_data.items():
        count = len(data["opt_scores"])
        avg_opt = round(sum(data["opt_scores"]) / count, 4) if count else 0
        avg_edge = round(sum(data["edge_scores"]) / count, 4) if count else 0
        avg_pattern = round(sum(data["pattern_scores"]) / count, 4) if count else 0
        avg_overall = round((avg_opt + avg_edge + avg_pattern) / 3.0, 4)

        topic_breakdown.append(TopicMetric(
            topic=topic,
            total_submissions=count,
            avg_optimization_score=avg_opt,
            avg_edge_case_score=avg_edge,
            avg_pattern_score=avg_pattern,
            avg_overall_score=avg_overall,
        ))

    # Sort by total submissions descending
    topic_breakdown.sort(key=lambda t: t.total_submissions, reverse=True)

    # --- Recent submissions (last 20) ---
    recent = []
    for s in submissions[:20]:
        recent.append(RecentSubmission(
            submission_id=s["id"],
            problem_id=s["problem_id"],
            language=s.get("language", ""),
            optimization_score=s.get("optimization_score", 0),
            edge_case_score=s.get("edge_case_score", 0),
            pattern_understanding_score=s.get("pattern_understanding_score", 0),
            weak_topic=s.get("weak_topic"),
            created_at=s.get("created_at", ""),
        ))

    # --- Pending revisions count ---
    revision_result = db.table("revision_queue").select(
        "id", count="exact"
    ).eq("user_id", user_id).eq("status", "Pending").execute()

    pending_revisions = revision_result.count if revision_result.count else 0

    # --- Improvement trends from learning_insights ---
    insights_result = db.table("learning_insights").select("*").eq(
        "user_id", user_id
    ).execute()

    improvement_trends = {}
    if insights_result.data:
        improvement_trends = insights_result.data[0].get("improvement_trends", {}) or {}

    return AnalyticsResponse(
        user_id=user_id,
        total_submissions=total_submissions,
        total_problems_solved=total_problems_solved,
        weak_topics=user_weak_topics,
        topic_breakdown=topic_breakdown,
        recent_submissions=recent,
        pending_revisions=pending_revisions,
        current_level=current_level,
        improvement_trends=improvement_trends,
    )
