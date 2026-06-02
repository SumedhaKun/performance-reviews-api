from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import date
import sqlalchemy
from src.api.routes import auth
from src.api import db


class PerformanceReview(BaseModel):
    employee_id: int
    review_period_start: date
    review_period_end: date
    review_date: date
    reviewer_id: int
    overall_rating: int = Field(ge=1, le=5)
    category_1: int
    category_2: int
    category_3: int
    comment: str
    title_change: int = Field(ge=0, le=1)
    level_change: int = Field(ge=0, le=1)


class PerformanceReviewDraft(BaseModel):
    employee_id: int | None = None
    review_period_start: date | None = None
    review_period_end: date | None = None
    review_date: date | None = None
    reviewer_id: int | None = None
    overall_rating: int | None = None
    category_1: int | None = None
    category_2: int | None = None
    category_3: int | None = None
    comment: str | None = None
    title_change: int | None = None
    level_change: int | None = None

router = APIRouter(
    prefix="/performance_reviews",
    tags=["performance_reviews"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/")
def get_performance_reviews():
    """Get all performance reviews."""
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


@router.get("/{review_id}/")
def get_performance_review(review_id: int):
    """Get one performance review by id."""
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

@router.post("/draft", status_code=201)
def create_draft(performance_review: PerformanceReviewDraft):
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""
                INSERT INTO pr_draft (
                    employee_id,
                    review_period_start,
                    review_period_end,
                    review_date,
                    reviewer_id,
                    overall_rating,
                    category_1,
                    category_2,
                    category_3,
                    comment,
                    title_change,
                    level_change
                )
                VALUES (
                    :employee_id,
                    :review_period_start,
                    :review_period_end,
                    :review_date,
                    :reviewer_id,
                    :overall_rating,
                    :category_1,
                    :category_2,
                    :category_3,
                    :comment,
                    :title_change,
                    :level_change
                )
                RETURNING id
            """),
            performance_review.model_dump(),
        )

        draft_id = result.scalar_one()

    return {"id": draft_id}

@router.patch("/draft/{draft_id}")
def update_draft(
    draft_id: int,
    performance_review: PerformanceReviewDraft,
):
    values = performance_review.model_dump(exclude_unset=True)

    if not values:
        return {"success": True}

    set_clause = ", ".join(f"{key} = :{key}" for key in values)

    query = f"""
        UPDATE pr_draft
        SET {set_clause}
        WHERE id = :draft_id
    """

    values["draft_id"] = draft_id

    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text(query), values)

        if result.rowcount == 0:
            raise HTTPException(404, "Draft not found")

    return {"success": True}


@router.post("/submit/{draft_id}", status_code=201)
def submit_draft(draft_id: int):
    with db.engine.begin() as connection:
        draft = connection.execute(
            sqlalchemy.text("""
                SELECT *
                FROM pr_draft
                WHERE id = :draft_id
            """),
            {"draft_id": draft_id},
        ).mappings().first()

        if not draft:
            raise HTTPException(404, "Draft not found")

        review_id = connection.execute(
            sqlalchemy.text("""
                INSERT INTO performance_reviews (
                    employee_id,
                    review_period_start,
                    review_period_end,
                    review_date,
                    reviewer_id,
                    overall_rating,
                    category_1,
                    category_2,
                    category_3,
                    comment,
                    title_change,
                    level_change
                )
                VALUES (
                    :employee_id,
                    :review_period_start,
                    :review_period_end,
                    :review_date,
                    :reviewer_id,
                    :overall_rating,
                    :category_1,
                    :category_2,
                    :category_3,
                    :comment,
                    :title_change,
                    :level_change
                )
                RETURNING id
            """),
            dict(draft),
        ).scalar_one()

        connection.execute(
            sqlalchemy.text("""
                DELETE FROM pr_draft
                WHERE id = :draft_id
            """),
            {"draft_id": draft_id},
        )

    return {"id": review_id}

@router.post("/", status_code=201)
def create_performance_review(performance_review: PerformanceReview):
    """Create a performance review."""
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


@router.delete("/{review_id}/", status_code=204)
def delete_performance_row(review_id: int):
    """Delete a performance review."""
    with db.engine.begin() as connection:
        review_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM performance_reviews
                WHERE id = :review_id
                """
            ),
            {"review_id": review_id},
        ).one_or_none()

        if review_exists is None:
            raise HTTPException(status_code=404, detail="Review not found")

        connection.execute(
            sqlalchemy.text("""
                DELETE FROM performance_reviews
                WHERE id = :review_id
            """),
            {"review_id": review_id},
        )


@router.patch("/{review_id}/", status_code=200)
def patch_performance_review(
    review_id: int,
    employee_id: int | None = None,
    review_period_start: date | None = None,
    review_period_end: date | None = None,
    review_date: date | None = None,
    reviewer_id: int | None = None,
    overall_rating: int | None = Query(default=None, ge=1, le=5),
    category_1: int | None = None,
    category_2: int | None = None,
    category_3: int | None = None,
    comment: str | None = None,
    title_change: int | None = None,
    level_change: int | None = None,
):
    """Update fields on a performance review."""
    update_fields = {
        "employee_id": employee_id,
        "review_period_start": review_period_start,
        "review_period_end": review_period_end,
        "review_date": review_date,
        "reviewer_id": reviewer_id,
        "overall_rating": overall_rating,
        "category_1": category_1,
        "category_2": category_2,
        "category_3": category_3,
        "comment": comment,
        "title_change": title_change,
        "level_change": level_change,
    }

    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    set_clause = ", ".join([f"{key} = :{key}" for key in update_fields.keys()])

    query = sqlalchemy.text(f"""
        UPDATE performance_reviews
        SET {set_clause}
        WHERE id = :review_id
        RETURNING id, employee_id, review_period_start, review_period_end,
            review_date, reviewer_id, overall_rating, category_1, category_2,
            category_3, comment, title_change, level_change
    """)

    update_fields["review_id"] = review_id

    with db.engine.begin() as connection:
        updated_review = (
            connection.execute(query, update_fields).mappings().one_or_none()
        )

    if updated_review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    return dict(updated_review)
