from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.api.routes import auth
import sqlalchemy

from src.api import db


class NewComment(BaseModel):
    employeeId: int
    subject: str
    comment: str
    authorId: int


def format_comment(comment):
    return {
        "id": comment["id"],
        "employeeId": comment["employee_id"],
        "subject": comment["subject"],
        "comment": comment["content"],
        "authorId": comment["commenter_id"],
        "createdAt": comment["created_at"],
    }


router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/")
def get_comments(authorId: Optional[int] = None, employeeId: Optional[int] = None):
    """Get comments by author or employee."""
    if authorId is None and employeeId is None:
        raise HTTPException(
            status_code=400,
            detail="At least one query parameter is required: authorId or employeeId",
        )

    filters = []
    params = {}

    if authorId is not None:
        filters.append("commenter_id = :author_id")
        params["author_id"] = authorId

    if employeeId is not None:
        filters.append("employee_id = :employee_id")
        params["employee_id"] = employeeId

    with db.engine.begin() as connection:
        if authorId is not None:
            author_exists = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT 1
                    FROM employees
                    WHERE id = :author_id
                    """
                ),
                {"author_id": authorId},
            ).one_or_none()

            if author_exists is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Author employee {authorId} not found",
                )

        if employeeId is not None:
            employee_exists = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT 1
                    FROM employees
                    WHERE id = :employee_id
                    """
                ),
                {"employee_id": employeeId},
            ).one_or_none()

            if employee_exists is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Employee {employeeId} not found",
                )

        comments = (
            connection.execute(
                sqlalchemy.text(
                    f"""
                SELECT id, employee_id, subject, commenter_id, content, created_at
                FROM comments
                WHERE {" AND ".join(filters)}
                ORDER BY created_at DESC, id DESC
                """
                ),
                params,
            )
            .mappings()
            .all()
        )

    return [format_comment(comment) for comment in comments]


@router.get("/{comment_id}/")
def get_comment(comment_id: int):
    """Get one comment by id."""
    with db.engine.begin() as connection:
        comment = (
            connection.execute(
                sqlalchemy.text(
                    """
                SELECT id, employee_id, subject, commenter_id, content, created_at
                FROM comments
                WHERE id = :comment_id
                """
                ),
                {"comment_id": comment_id},
            )
            .mappings()
            .one_or_none()
        )

    if comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")

    return format_comment(comment)


@router.post("/", status_code=201)
def create_comment(new_comment: NewComment):
    """Create a comment."""
    with db.engine.begin() as connection:
        employee_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM employees
                WHERE id = :employee_id
                """
            ),
            {"employee_id": new_comment.employeeId},
        ).one_or_none()

        if employee_exists is None:
            raise HTTPException(
                status_code=404,
                detail=f"Employee {new_comment.employeeId} not found",
            )

        author_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM employees
                WHERE id = :author_id
                """
            ),
            {"author_id": new_comment.authorId},
        ).one_or_none()

        if author_exists is None:
            raise HTTPException(
                status_code=404,
                detail=f"Author employee {new_comment.authorId} not found",
            )

        comment = (
            connection.execute(
                sqlalchemy.text(
                    """
                INSERT INTO comments (
                    employee_id,
                    subject,
                    commenter_id,
                    content
                )
                VALUES (
                    :employee_id,
                    :subject,
                    :author_id,
                    :content
                )
                RETURNING id, employee_id, subject, commenter_id, content, created_at
                """
                ),
                {
                    "employee_id": new_comment.employeeId,
                    "subject": new_comment.subject,
                    "author_id": new_comment.authorId,
                    "content": new_comment.comment,
                },
            )
            .mappings()
            .one()
        )

    return format_comment(comment)


@router.delete("/{comment_id}/", status_code=204)
def delete_comment(comment_id: int):
    """Delete a comment."""
    with db.engine.begin() as connection:
        comment_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM comments
                WHERE id = :comment_id
                """
            ),
            {"comment_id": comment_id},
        ).one_or_none()

        if comment_exists is None:
            raise HTTPException(status_code=404, detail="Comment not found")

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM comments
                WHERE id = :comment_id
                """
            ),
            {"comment_id": comment_id},
        )
