from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import sqlalchemy
from src.api.routes import auth
from src.api import db
from src.api.routes.helpers import ensure_resource_exists


class PerformanceReview(BaseModel):
    employee_id: int
    review_period_start: date
    review_period_end: date
    review_date: date
    reviewer_id: int
    overall_rating: int = Field(ge=1, le=10)
    category_1: int = Field(ge=1, le=10)
    category_2: int = Field(ge=1, le=10)
    category_3: int = Field(ge=1, le=10)
    comment: str
    title_change: bool = False
    level_change: bool = False


class PerformanceReviewDraft(BaseModel):
    employee_id: int | None = None
    review_period_start: date | None = None
    review_period_end: date | None = None
    review_date: date | None = None
    reviewer_id: int | None = None
    overall_rating: int | None = None
    category_1: int | None = Field(default=None, ge=1, le=10)
    category_2: int | None = Field(default=None, ge=1, le=10)
    category_3: int | None = Field(default=None, ge=1, le=10)
    comment: str | None = None
    title_change: bool | None = None
    level_change: bool | None = None


class PerformanceReviewResponse(PerformanceReview):
    id: int

class IdResponse(BaseModel):
    id: int


class DraftResponse(BaseModel):
    id: int


class SuccessResponse(BaseModel):
    success: bool


router = APIRouter(
    prefix="/performance_reviews",
    tags=["performance_reviews"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/", response_model=list[PerformanceReviewResponse], status_code=status.HTTP_200_OK)
def get_performance_reviews(reviewerId: Optional[int] = None, employeeId: Optional[int] = None):
    """Get all performance reviews."""
    if reviewerId is None and employeeId is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one query parameter is required: reviewerId or employeeId",
        )

    filters = []
    params = {}

    if reviewerId is not None:
        filters.append("reviewer_id = :reviewer_id")
        params["reviewer_id"] = reviewerId

    if employeeId is not None:
        filters.append("employee_id = :employee_id")
        params["employee_id"] = employeeId


    with db.engine.begin() as connection:
        where_clause = " AND ".join(filters)
        performance_reviews = (
            connection.execute(
                sqlalchemy.text(
                    """
                SELECT id, employee_id, review_period_start, review_period_end,
                    review_date, reviewer_id, overall_rating, category_1, category_2,
                    category_3, comment, title_change, level_change
                FROM performance_reviews
                WHERE """ + where_clause + """
                ORDER BY review_date DESC, id DESC
                """
                ), params
            )
            .mappings()
        )

    return [dict(review) for review in performance_reviews]

@router.get("/{review_id}/", response_model=PerformanceReviewResponse, status_code=200)
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
            .one_or_none()
        )

    if performance_review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    return PerformanceReviewResponse(
        id = performance_review.id,
        employee_id = performance_review.employee_id,
        review_period_start = performance_review.review_period_start,
        review_period_end = performance_review.review_period_end,
        review_date = performance_review.review_date,
        reviewer_id = performance_review.reviewer_id,
        overall_rating = performance_review.overall_rating,
        category_1 = performance_review.category_1,
        category_2 = performance_review.category_2,
        category_3 = performance_review.category_3,
        comment = performance_review.comment,
        title_change = performance_review.title_change,
        level_change = performance_review.level_change
    )

@router.post("/draft", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
def create_draft(performance_review: PerformanceReviewDraft):
    with db.engine.begin() as connection:
        ensure_resource_exists(
            connection,
            "employees",
            performance_review.employee_id,
            "Reviewed employee not found"
        )

        ensure_resource_exists(
            connection,
            "employees",
            performance_review.reviewer_id,
            "Reviewer not found"
        )

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

    return IdResponse(id=draft_id)

@router.get("/draft/{draft_id}/", response_model=PerformanceReviewDraft, status_code=status.HTTP_200_OK)
def get_draft(
    draft_id: int
):
    with db.engine.begin() as connection:
        performance_review = (
            connection.execute(
                sqlalchemy.text(
                    """
                SELECT employee_id, review_period_start, review_period_end,
                    review_date, reviewer_id, overall_rating, category_1, category_2,
                    category_3, comment, title_change, level_change
                FROM pr_draft
                WHERE id = :draft_id
                """
                ),
                {"draft_id": draft_id},
            )
            .one_or_none()
        )

    if performance_review is None:
        raise HTTPException(status_code=404, detail="Review not found")

    return PerformanceReviewDraft(
        employee_id = performance_review.employee_id,
        review_period_start = performance_review.review_period_start,
        review_period_end = performance_review.review_period_end,
        review_date = performance_review.review_date,
        reviewer_id = performance_review.reviewer_id,
        overall_rating = performance_review.overall_rating,
        category_1 = performance_review.category_1,
        category_2 = performance_review.category_2,
        category_3 = performance_review.category_3,
        comment = performance_review.comment,
        title_change = performance_review.title_change,
        level_change = performance_review.level_change
    )
    

@router.patch("/draft/{draft_id}/", response_model=SuccessResponse, status_code=status.HTTP_200_OK)
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


@router.post("/submit/{draft_id}", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
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

    return IdResponse(id=review_id)

@router.post("/", response_model=PerformanceReviewResponse, status_code=status.HTTP_201_CREATED)
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
            .one()
        )

    return PerformanceReviewResponse(
        id = performance_review.id,
        employee_id = performance_review.employee_id,
        review_period_start = performance_review.review_period_start,
        review_period_end = performance_review.review_period_end,
        review_date = performance_review.review_date,
        reviewer_id = performance_review.reviewer_id,
        overall_rating = performance_review.overall_rating,
        category_1 = performance_review.category_1,
        category_2 = performance_review.category_2,
        category_3 = performance_review.category_3,
        comment = performance_review.comment,
        title_change = performance_review.title_change,
        level_change = performance_review.level_change
    )


@router.delete("/{review_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_performance_row(review_id: int):
    """Delete a performance review."""
    with db.engine.begin() as connection:
        ensure_resource_exists(
            connection,
            "performance_reviews",
            review_id,
            "Review not found"
        )

        connection.execute(
            sqlalchemy.text("""
                DELETE FROM performance_reviews
                WHERE id = :review_id
            """),
            {"review_id": review_id},
        )


@router.patch("/{review_id}/", response_model=PerformanceReviewResponse, status_code=status.HTTP_200_OK,)
def patch_performance_review(
    review_id: int,
    new_review: PerformanceReviewDraft
    #employee_id: int | None = None,
    #review_period_start: date | None = None,
    #review_period_end: date | None = None,
    #review_date: date | None = None,
    #reviewer_id: int | None = None,
    #overall_rating: int | None = Query(default=None, ge=1, le=10),
    #category_1: int | None = None,
    #category_2: int | None = None,
    #category_3: int | None = None,
    #comment: str | None = None,
    #title_change: bool | None = None,
    #level_change: bool | None = None,"""
):
    """Update fields on a performance review."""
    update_fields = {
        "employee_id": new_review.employee_id,
        "review_period_start": new_review.review_period_start,
        "review_period_end": new_review.review_period_end,
        "review_date": new_review.review_date,
        "reviewer_id": new_review.reviewer_id,
        "overall_rating": new_review.overall_rating,
        "category_1": new_review.category_1,
        "category_2": new_review.category_2,
        "category_3": new_review.category_3,
        "comment": new_review.comment,
        "title_change": new_review.title_change,
        "level_change": new_review.level_change,
    }

    update_fields = {k: v for k, v in update_fields.items() if v is not None}

    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")

    allowed_columns = {
        "employee_id", "review_period_start", "review_period_end",
        "review_date", "reviewer_id", "overall_rating", "category_1",
        "category_2", "category_3", "comment", "title_change", "level_change"
    }
    
    # Validate that all keys are allowed columns
    for key in update_fields.keys():
        if key not in allowed_columns:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid field: {key}")

    set_clause = ", ".join([f"{key} = :{key}" for key in update_fields.keys()])

    query = sqlalchemy.text(
        """
        UPDATE performance_reviews
        SET """ + set_clause + """
        WHERE id = :review_id
        RETURNING id, employee_id, review_period_start, review_period_end,
            review_date, reviewer_id, overall_rating, category_1, category_2,
            category_3, comment, title_change, level_change
    """
    )

    update_fields["review_id"] = review_id

    with db.engine.begin() as connection:
        if new_review.employee_id is not None:
            ensure_resource_exists(
                connection,
                "employees",
                new_review.employee_id,
                "Reviewed employee not found"
            )
        if new_review.reviewer_id is not None:
            ensure_resource_exists(
                connection,
                "employees",
                new_review.reviewer_id,
                "Reviewer not found"
            )
        updated_review = (
            connection.execute(query, update_fields).one_or_none()
        )

    if updated_review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")

    return PerformanceReviewResponse(
        id = updated_review.id,
        employee_id = updated_review.employee_id,
        review_period_start = updated_review.review_period_start,
        review_period_end = updated_review.review_period_end,
        review_date = updated_review.review_date,
        reviewer_id = updated_review.reviewer_id,
        overall_rating = updated_review.overall_rating,
        category_1 = updated_review.category_1,
        category_2 = updated_review.category_2,
        category_3 = updated_review.category_3,
        comment = updated_review.comment,
        title_change = updated_review.title_change,
        level_change = updated_review.level_change
    )
