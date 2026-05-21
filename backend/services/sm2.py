"""
SM-2 Spaced Repetition Algorithm.

Implements the SuperMemo SM-2 algorithm for scheduling revision problems.
The same algorithm that powers Anki — adapted here to use code review scores
as the quality grade.

Reference: https://www.supermemo.com/en/blog/application-of-a-computer-to-improve-the-results-obtained-in-working-with-the-supermemo-method

Grade mapping from AI code review scores:
    average_score (0.0 - 1.0) -> quality grade q (0 - 5)
    q >= 3: Correct response -> increase interval
    q <  3: Incorrect -> reset to beginning
"""
import math
from datetime import date, timedelta
from dataclasses import dataclass


@dataclass
class SM2Result:
    """Result of an SM-2 calculation."""
    repetition: int
    easiness_factor: float
    interval_days: int
    scheduled_date: date


def scores_to_grade(
    optimization_score: float,
    edge_case_score: float,
    pattern_understanding_score: float
) -> int:
    """
    Convert the three AI review scores (each 0.0-1.0) into an SM-2 grade (0-5).
    
    The average of the three scores is scaled to a 0-5 integer:
        0 - Complete blackout
        1 - Incorrect, but remembered something
        2 - Incorrect, but easy to recall correct answer
        3 - Correct with serious difficulty
        4 - Correct with some hesitation
        5 - Perfect response
    """
    average = (optimization_score + edge_case_score + pattern_understanding_score) / 3.0
    grade = math.floor(average * 5 + 0.5)
    return max(0, min(5, grade))


def calculate_sm2(
    grade: int,
    repetition: int = 0,
    easiness_factor: float = 2.5,
    interval: int = 1
) -> SM2Result:
    """
    Calculate the next SM-2 scheduling state.
    
    Args:
        grade: Quality of response (0-5), derived from code review scores
        repetition: Current repetition count (n)
        easiness_factor: Current easiness factor (EF), minimum 1.3
        interval: Current interval in days
    
    Returns:
        SM2Result with updated repetition, easiness_factor, interval, and next date
    """
    # Successful recall (grade >= 3)
    if grade >= 3:
        if repetition == 0:
            interval = 1
        elif repetition == 1:
            interval = 6
        else:
            interval = math.ceil(interval * easiness_factor)
        repetition += 1
    else:
        # Failed recall — reset
        repetition = 0
        interval = 1

    # Update easiness factor
    easiness_factor = easiness_factor + (
        0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)
    )
    easiness_factor = max(1.3, easiness_factor)

    scheduled_date = date.today() + timedelta(days=interval)

    return SM2Result(
        repetition=repetition,
        easiness_factor=round(easiness_factor, 4),
        interval_days=interval,
        scheduled_date=scheduled_date,
    )
