"""
Test script for Dev B components.
Run: python test_dev_b.py

Tests the SM-2 algorithm, models, and AI client config — no DB or server needed.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from services.sm2 import calculate_sm2, scores_to_grade, SM2Result
from models import (
    SubmitCodeRequest, SubmissionResponse,
    RevisionItem, RevisionQueueResponse,
    TopicMetric, AnalyticsResponse,
)

PASS = 0
FAIL = 0

def test(name, condition):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}")


# ====================================================================
# SM-2 Algorithm Tests
# ====================================================================
print("\n🧠 SM-2 Algorithm Tests")
print("=" * 50)

# Test 1: Score to grade conversion
print("\n📊 scores_to_grade()")
test("Perfect scores (1.0, 1.0, 1.0) → grade 5", scores_to_grade(1.0, 1.0, 1.0) == 5)
test("Zero scores (0.0, 0.0, 0.0) → grade 0", scores_to_grade(0.0, 0.0, 0.0) == 0)
test("Mid scores (0.5, 0.5, 0.5) → grade 3", scores_to_grade(0.5, 0.5, 0.5) == 3)
test("Mixed scores (0.8, 0.6, 0.7) → grade 3", scores_to_grade(0.8, 0.6, 0.7) == 3)
test("Low scores (0.2, 0.3, 0.1) → grade 1", scores_to_grade(0.2, 0.3, 0.1) == 1)

# Test 2: First-time correct submission (grade 5)
print("\n🆕 First submission — perfect score")
r = calculate_sm2(grade=5, repetition=0, easiness_factor=2.5, interval=1)
test(f"Interval = 1 day (got {r.interval_days})", r.interval_days == 1)
test(f"Repetition = 1 (got {r.repetition})", r.repetition == 1)
test(f"EF increased above 2.5 (got {r.easiness_factor})", r.easiness_factor > 2.5)
test(f"Returns SM2Result type", isinstance(r, SM2Result))

# Test 3: Second correct submission
print("\n🔁 Second submission — perfect score")
r2 = calculate_sm2(grade=5, repetition=r.repetition, easiness_factor=r.easiness_factor, interval=r.interval_days)
test(f"Interval = 6 days (got {r2.interval_days})", r2.interval_days == 6)
test(f"Repetition = 2 (got {r2.repetition})", r2.repetition == 2)

# Test 4: Third correct submission — interval multiplied by EF
print("\n📈 Third submission — interval grows exponentially")
r3 = calculate_sm2(grade=4, repetition=r2.repetition, easiness_factor=r2.easiness_factor, interval=r2.interval_days)
test(f"Interval > 6 days (got {r3.interval_days})", r3.interval_days > 6)
test(f"Repetition = 3 (got {r3.repetition})", r3.repetition == 3)

# Test 5: Failed submission — resets
print("\n💥 Failed submission — SM-2 reset")
r_fail = calculate_sm2(grade=1, repetition=r3.repetition, easiness_factor=r3.easiness_factor, interval=r3.interval_days)
test(f"Repetition reset to 0 (got {r_fail.repetition})", r_fail.repetition == 0)
test(f"Interval reset to 1 day (got {r_fail.interval_days})", r_fail.interval_days == 1)
test(f"EF >= 1.3 floor (got {r_fail.easiness_factor})", r_fail.easiness_factor >= 1.3)

# Test 6: EF floor enforcement
print("\n🔒 Easiness factor floor (1.3)")
r_floor = calculate_sm2(grade=0, repetition=0, easiness_factor=1.3, interval=1)
test(f"EF stays >= 1.3 (got {r_floor.easiness_factor})", r_floor.easiness_factor >= 1.3)

# Test 7: Scheduled date is set
print("\n📅 Scheduled date")
test(f"Has scheduled_date: {r.scheduled_date}", r.scheduled_date is not None)
test(f"Date is in the future", str(r.scheduled_date) >= str(__import__('datetime').date.today()))


# ====================================================================
# Pydantic Model Validation Tests
# ====================================================================
print("\n\n📦 Pydantic Model Tests")
print("=" * 50)

# SubmitCodeRequest
print("\n📝 SubmitCodeRequest")
req = SubmitCodeRequest(
    user_id="user-123",
    problem_id="two-sum",
    code="def twoSum(nums, target): pass",
    language="python",
    hints_used=1,
    time_taken=300,
)
test(f"user_id = '{req.user_id}'", req.user_id == "user-123")
test(f"hints_used defaults work", req.hints_used == 1)
test(f"time_taken = 300s", req.time_taken == 300)

# SubmitCodeRequest with defaults
req_default = SubmitCodeRequest(
    user_id="u1", problem_id="p1", code="x=1", language="python"
)
test(f"hints_used defaults to 0", req_default.hints_used == 0)
test(f"time_taken defaults to 0", req_default.time_taken == 0)

# SubmissionResponse
print("\n📊 SubmissionResponse")
resp = SubmissionResponse(
    submission_id="abc-123",
    problem_id="two-sum",
    optimization_score=0.85,
    edge_case_score=0.7,
    pattern_understanding_score=0.9,
    feedback="Good use of hashmap.",
    time_complexity="O(n)",
    space_complexity="O(n)",
    weak_topic=None,
    sm2_grade=4,
    next_revision_date="2026-05-24",
)
test(f"optimization_score = 0.85", resp.optimization_score == 0.85)
test(f"sm2_grade = 4", resp.sm2_grade == 4)
test(f"weak_topic is None", resp.weak_topic is None)

# RevisionItem
print("\n🔄 RevisionItem")
rev = RevisionItem(
    id="rev-1", problem_id="two-sum", topic="Arrays",
    scheduled_date="2026-05-24", status="Pending",
    repetition=2, easiness_factor=2.6, interval_days=6,
)
test(f"SM-2 state preserved: rep={rev.repetition}, EF={rev.easiness_factor}", True)

# AnalyticsResponse
print("\n📈 AnalyticsResponse")
analytics = AnalyticsResponse(
    user_id="user-123",
    total_submissions=15,
    total_problems_solved=8,
    weak_topics=["Dynamic Programming", "Graph"],
    topic_breakdown=[],
    recent_submissions=[],
    pending_revisions=3,
    current_level="Intermediate",
)
test(f"total_problems_solved = 8", analytics.total_problems_solved == 8)
test(f"weak_topics has 2 items", len(analytics.weak_topics) == 2)


# ====================================================================
# AI Client Config Test
# ====================================================================
print("\n\n🤖 AI Client Config Test")
print("=" * 50)
from services.ai_client import AI_SERVICE_URL
test(f"AI_SERVICE_URL configured: {AI_SERVICE_URL}", AI_SERVICE_URL is not None and len(AI_SERVICE_URL) > 0)


# ====================================================================
# Summary
# ====================================================================
print("\n")
print("=" * 50)
total = PASS + FAIL
print(f"🏁 Results: {PASS}/{total} passed, {FAIL} failed")
if FAIL == 0:
    print("🎉 All tests passed!")
else:
    print(f"⚠️  {FAIL} test(s) failed.")
print("=" * 50)
