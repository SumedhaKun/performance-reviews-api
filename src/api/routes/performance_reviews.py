from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import sqlalchemy
from src.api.routes import auth
from src.api import db
from src.api.routes.helpers import ensure_resource_exists


review_needs = (
    "employee_id",
    "review_period_start",
    "review_period_end",
    "review_date",
    "reviewer_id",
    "overall_rating",
    "category_1",
    "category_2",
    "category_3",
    "comment",
)

ratings = (
    "overall_rating",
    "category_1",
    "category_2",
    "category_3",
)


def validate_review_date_order(
    review_period_start: date | None,
    review_period_end: date | None,
    review_date: date | None,
) -> None:
    if (
        review_period_start is not None
        and review_period_end is not None
        and review_period_start > review_period_end
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="review_period_start must be on or before review_period_end",
        )

    if (
        review_period_end is not None
        and review_date is not None
        and review_period_end > review_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="review_period_end must be on or before review_date",
        )


def ensure_review_employees_exist(
    connection,
    employee_id: int | None,
    reviewer_id: int | None,
):
    if employee_id is not None:
        ensure_resource_exists(
            connection, "employees", employee_id, "Reviewed employee not found"
        )

    if reviewer_id is not None:
        ensure_resource_exists(
            connection, "employees", reviewer_id, "Reviewer not found"
        )


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
    overall_rating: int | None = Field(default=None, ge=1, le=10)
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


class SuccessResponse(BaseModel):
    success: bool


router = APIRouter(
    prefix="/performance_reviews",
    tags=["performance_reviews"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get(
    "/", response_model=list[PerformanceReviewResponse], status_code=status.HTTP_200_OK
)
def get_performance_reviews(
    reviewerId: Optional[int] = None, employeeId: Optional[int] = None
):
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
        performance_reviews = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, employee_id, review_period_start, review_period_end,
                    review_date, reviewer_id, overall_rating, category_1, category_2,
                    category_3, comment, title_change, level_change
                FROM performance_reviews
                WHERE """
                + where_clause
                + """
                ORDER BY review_date DESC, id DESC
                """
            ),
            params,
        ).mappings()

    return [dict(review) for review in performance_reviews]


@router.get(
    "/{review_id}/",
    response_model=PerformanceReviewResponse,
    status_code=status.HTTP_200_OK,
)
def get_performance_review(review_id: int):
    """Get one performance review by id."""
    with db.engine.begin() as connection:
        performance_review = connection.execute(
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
        ).one_or_none()

    if performance_review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    return PerformanceReviewResponse(
        id=performance_review.id,
        employee_id=performance_review.employee_id,
        review_period_start=performance_review.review_period_start,
        review_period_end=performance_review.review_period_end,
        review_date=performance_review.review_date,
        reviewer_id=performance_review.reviewer_id,
        overall_rating=performance_review.overall_rating,
        category_1=performance_review.category_1,
        category_2=performance_review.category_2,
        category_3=performance_review.category_3,
        comment=performance_review.comment,
        title_change=performance_review.title_change,
        level_change=performance_review.level_change,
    )


@router.post("/draft", response_model=IdResponse, status_code=status.HTTP_201_CREATED)
def create_draft(performance_review: PerformanceReviewDraft):
    validate_review_date_order(
        performance_review.review_period_start,
        performance_review.review_period_end,
        performance_review.review_date,
    )

    with db.engine.begin() as connection:
        ensure_review_employees_exist(
            connection,
            performance_review.employee_id,
            performance_review.reviewer_id,
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

        draft_id = result.scalar_one()

    return IdResponse(id=draft_id)


@router.get(
    "/draft/{draft_id}/",
    response_model=PerformanceReviewDraft,
    status_code=status.HTTP_200_OK,
)
def get_draft(draft_id: int):
    with db.engine.begin() as connection:
        performance_review = connection.execute(
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
        ).one_or_none()

    if performance_review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )

    return PerformanceReviewDraft(
        employee_id=performance_review.employee_id,
        review_period_start=performance_review.review_period_start,
        review_period_end=performance_review.review_period_end,
        review_date=performance_review.review_date,
        reviewer_id=performance_review.reviewer_id,
        overall_rating=performance_review.overall_rating,
        category_1=performance_review.category_1,
        category_2=performance_review.category_2,
        category_3=performance_review.category_3,
        comment=performance_review.comment,
        title_change=performance_review.title_change,
        level_change=performance_review.level_change,
    )


@router.patch(
    "/draft/{draft_id}/", response_model=SuccessResponse, status_code=status.HTTP_200_OK
)
def update_draft(
    draft_id: int,
    performance_review: PerformanceReviewDraft,
):
    values = {
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
    }

    values = {key: value for key, value in values.items() if value is not None}

    if not values:
        return {"success": True}

    with db.engine.begin() as connection:
        existing_draft = (
            connection.execute(
                sqlalchemy.text("""
                    SELECT employee_id, review_period_start, review_period_end,
                        review_date, reviewer_id, overall_rating, category_1,
                        category_2, category_3, comment, title_change,
                        level_change
                    FROM pr_draft
                    WHERE id = :draft_id
                """),
                {"draft_id": draft_id},
            )
            .mappings()
            .one_or_none()
        )

        if existing_draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found",
            )

        ensure_review_employees_exist(
            connection,
            values.get("employee_id"),
            values.get("reviewer_id"),
        )

        updated_values = dict(existing_draft)
        updated_values.update(values)
        validate_review_date_order(
            updated_values["review_period_start"],
            updated_values["review_period_end"],
            updated_values["review_date"],
        )

        set_clause = ", ".join(f"{key} = :{key}" for key in values)

        query = f"""
            UPDATE pr_draft
            SET {set_clause}
            WHERE id = :draft_id
        """

        values["draft_id"] = draft_id

        result = connection.execute(sqlalchemy.text(query), values)

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
            )

    return {"success": True}


@router.post(
    "/submit/{draft_id}", response_model=IdResponse, status_code=status.HTTP_201_CREATED
)
def submit_draft(draft_id: int):
    with db.engine.begin() as connection:

        submitted = (
            connection.execute(
                sqlalchemy.text("""
                SELECT review_id
                FROM submitted_pr_drafts
                WHERE draft_id = :draft_id
            """),
                {"draft_id": draft_id},
            )
            .mappings()
            .one_or_none()
        )

        if submitted is not None:
            print(submitted)
            return IdResponse(id=submitted["review_id"])

        draft = (
            connection.execute(
                sqlalchemy.text("""
                SELECT *
                FROM pr_draft
                WHERE id = :draft_id
            """),
                {"draft_id": draft_id},
            )
            .mappings()
            .first()
        )

        if not draft:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
            )

        draft_values = dict(draft)
        missing_fields = [
            field for field in review_needs if draft_values.get(field) is None
        ]
        if missing_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Draft is missing required fields: {', '.join(missing_fields)}",
            )

        for field in ratings:
            if draft_values[field] < 1 or draft_values[field] > 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{field} must be between 1 and 10",
                )

        validate_review_date_order(
            draft_values["review_period_start"],
            draft_values["review_period_end"],
            draft_values["review_date"],
        )

        draft_values["title_change"] = (
            draft_values["title_change"]
            if draft_values["title_change"] is not None
            else False
        )
        draft_values["level_change"] = (
            draft_values["level_change"]
            if draft_values["level_change"] is not None
            else False
        )
        ensure_review_employees_exist(
            connection,
            draft_values["employee_id"],
            draft_values["reviewer_id"],
        )

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
            {
                "employee_id": draft_values["employee_id"],
                "review_period_start": draft_values["review_period_start"],
                "review_period_end": draft_values["review_period_end"],
                "review_date": draft_values["review_date"],
                "reviewer_id": draft_values["reviewer_id"],
                "overall_rating": draft_values["overall_rating"],
                "category_1": draft_values["category_1"],
                "category_2": draft_values["category_2"],
                "category_3": draft_values["category_3"],
                "comment": draft_values["comment"],
                "title_change": draft_values["title_change"],
                "level_change": draft_values["level_change"],
            },
        ).scalar_one()

        connection.execute(
            sqlalchemy.text("""
                DELETE FROM pr_draft
                WHERE id = :draft_id
            """),
            {"draft_id": draft_id},
        )

        connection.execute(
            sqlalchemy.text("""
                INSERT INTO submitted_pr_drafts (draft_id, review_id)
                VALUES (:draft_id, :review_id)
            """),
            {
                "draft_id": draft_id,
                "review_id": review_id,
            },
        )

    return IdResponse(id=review_id)


@router.post(
    "/", response_model=PerformanceReviewResponse, status_code=status.HTTP_201_CREATED
)
def create_performance_review(performance_review: PerformanceReview):
    """Create a performance review."""
    validate_review_date_order(
        performance_review.review_period_start,
        performance_review.review_period_end,
        performance_review.review_date,
    )

    with db.engine.begin() as connection:
        ensure_review_employees_exist(
            connection,
            performance_review.employee_id,
            performance_review.reviewer_id,
        )

        performance_review = connection.execute(
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
        ).one()

    return PerformanceReviewResponse(
        id=performance_review.id,
        employee_id=performance_review.employee_id,
        review_period_start=performance_review.review_period_start,
        review_period_end=performance_review.review_period_end,
        review_date=performance_review.review_date,
        reviewer_id=performance_review.reviewer_id,
        overall_rating=performance_review.overall_rating,
        category_1=performance_review.category_1,
        category_2=performance_review.category_2,
        category_3=performance_review.category_3,
        comment=performance_review.comment,
        title_change=performance_review.title_change,
        level_change=performance_review.level_change,
    )


@router.delete("/{review_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_performance_row(review_id: int):
    """Delete a performance review."""
    with db.engine.begin() as connection:
        ensure_resource_exists(
            connection, "performance_reviews", review_id, "Review not found"
        )

        connection.execute(
            sqlalchemy.text("""
                DELETE FROM performance_reviews
                WHERE id = :review_id
            """),
            {"review_id": review_id},
        )


@router.patch(
    "/{review_id}/",
    response_model=PerformanceReviewResponse,
    status_code=status.HTTP_200_OK,
)
def patch_performance_review(review_id: int, new_review: PerformanceReviewDraft):
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update",
        )

    allowed_columns = {
        "employee_id",
        "review_period_start",
        "review_period_end",
        "review_date",
        "reviewer_id",
        "overall_rating",
        "category_1",
        "category_2",
        "category_3",
        "comment",
        "title_change",
        "level_change",
    }

    # Validate that all keys are allowed columns
    for key in update_fields.keys():
        if key not in allowed_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid field: {key}"
            )

    set_clause = ", ".join([f"{key} = :{key}" for key in update_fields.keys()])

    query = sqlalchemy.text(
        """
        UPDATE performance_reviews
        SET """
        + set_clause
        + """
        WHERE id = :review_id
        RETURNING id, employee_id, review_period_start, review_period_end,
            review_date, reviewer_id, overall_rating, category_1, category_2,
            category_3, comment, title_change, level_change
    """
    )

    update_fields["review_id"] = review_id

    with db.engine.begin() as connection:
        existing_review = (
            connection.execute(
                sqlalchemy.text("""
                    SELECT id, employee_id, review_period_start, review_period_end,
                        review_date, reviewer_id, overall_rating, category_1,
                        category_2, category_3, comment, title_change,
                        level_change
                    FROM performance_reviews
                    WHERE id = :review_id
                """),
                {"review_id": review_id},
            )
            .mappings()
            .one_or_none()
        )

        if existing_review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
            )

        ensure_review_employees_exist(
            connection,
            new_review.employee_id,
            new_review.reviewer_id,
        )

        merged_review = dict(existing_review)
        merged_review.update(update_fields)
        validate_review_date_order(
            merged_review["review_period_start"],
            merged_review["review_period_end"],
            merged_review["review_date"],
        )

        updated_review = connection.execute(query, update_fields).one_or_none()

    return PerformanceReviewResponse(
        id=updated_review.id,
        employee_id=updated_review.employee_id,
        review_period_start=updated_review.review_period_start,
        review_period_end=updated_review.review_period_end,
        review_date=updated_review.review_date,
        reviewer_id=updated_review.reviewer_id,
        overall_rating=updated_review.overall_rating,
        category_1=updated_review.category_1,
        category_2=updated_review.category_2,
        category_3=updated_review.category_3,
        comment=updated_review.comment,
        title_change=updated_review.title_change,
        level_change=updated_review.level_change,
    )
