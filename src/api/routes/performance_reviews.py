from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
import sqlalchemy

from src.api import db

router = APIRouter()


class PerformanceReview(BaseModel):
    employee_id: int
    review_period_start: datetime
    review_period_end: datetime
    review_date: datetime
    reviewer_id: int
    overall_rating: int
    category_1: int
    category_2: int
    category_3: int
    comment: str
    title_change: int
    level_change: int


@router.get("/performance_reviews")
def get_performance_reviews():
    print("hey")
    with db.engine.begin() as connection:
        performance_reviews = (
            connection.execute(
                sqlalchemy.text(
                    """
                SELECT id, employee_id, review_period_start, review_period_end,
                    review_date, reviewer_id, overall_rating, category_1, category_2,
                    category_3, comment, title_change, level_change
                FROM performance_reviews
                """
                ),
            )
            .mappings()
            .all()
        )

    return performance_reviews


@router.get("/performance_reviews/{review_id}")
def get_performance_review(review_id: int):
    with db.engine.begin() as connection:
        performance_review = (
            connection.execute(
                sqlalchemy.text(
                    """
                SELECT id, employee_id, review_period_start, review_period_end,
                    review_date, reviewer_id, overall_rating, category_1, category_2,
                    category_3, comment, title_change, level_change
                FROM performance_reviews
                WHERE id = :review_id
                """
                ),
                {"review_id": review_id},
            )
            .mappings()
            .one_or_none()
        )

    if performance_review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    return dict(performance_review)


@router.post("/performance_reviews", status_code=201)
def create_performance_review(performance_review: PerformanceReview):
    with db.engine.begin() as connection:
        performance_review = (
            connection.execute(
                sqlalchemy.text(
                    """
                INSERT INTO performance_reviews (
                    employee_id, review_period_start, review_period_end,
                    review_date, reviewer_id, overall_rating, category_1, category_2,
                    category_3, comment, title_change, level_change
                )
                VALUES (
                    :employee_id, :review_period_start, :review_period_end,
                    :review_date, :reviewer_id, :overall_rating, :category_1, :category_2,
                    :category_3, :comment, :title_change, :level_change
                )
                RETURNING id, employee_id, review_period_start, review_period_end,
                    review_date, reviewer_id, overall_rating, category_1, category_2,
                    category_3, comment, title_change, level_change
                """
                ),
                {
                    "employee_id": performance_review.employee_id,
                    "review_period_start": performance_review.review_period_start,
                    "review_period_end": performance_review.review_period_end,
                    "review_date": performance_review.review_date,
                    "reviewer_id": performance_review.reviewer_id,
                    "overall_rating": performance_review.overall_rating,
                    "category_1": performance_review.category_1,
                    "category_2": performance_review.category_2,
                    "category_3": performance_review.category_3,
                    "comment": performance_review.comment,
                    "title_change": performance_review.title_change,
                    "level_change": performance_review.level_change,
                },
            )
            .mappings()
            .one()
        )

    return dict(performance_review)


@router.delete("/performance_reviews/{review_id}", status_code=204)
def delete_performance_row(review_id: int):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text("""
                DELETE FROM performance_reviews
                WHERE id = :review_id
            """),
            {"review_id": review_id},
        )
