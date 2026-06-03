from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from src.api.routes import auth
import sqlalchemy

from src.api import db
from src.api.routes.helpers import ensure_resource_exists, format_comment


class NewComment(BaseModel):
    employeeId: int
    subject: str
    comment: str
    authorId: int


class Comment(BaseModel):
    id: int
    employeeId: int
    subject: str
    comment: str
    authorId: int
    createdAt: datetime


router = APIRouter(
    prefix="/comments",
    tags=["comments"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/", response_model=list[Comment])
def get_comments(authorId: Optional[int] = None, employeeId: Optional[int] = None):
    """Get comments by author or employee."""
    if authorId is None and employeeId is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
            ensure_resource_exists(
                connection,
                "employees",
                authorId,
                f"Author employee {authorId} not found",
            )

        if employeeId is not None:
            ensure_resource_exists(
                connection,
                "employees",
                employeeId,
                f"Employee {employeeId} not found",
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


@router.get("/{comment_id}/", response_model=Comment, status_code=status.HTTP_200_OK)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    return format_comment(comment)


@router.post("/", response_model=Comment, status_code=status.HTTP_201_CREATED)
def create_comment(new_comment: NewComment):
    """Create a comment."""
    with db.engine.begin() as connection:
        ensure_resource_exists(
            connection,
            "employees",
            new_comment.employeeId,
            f"Employee {new_comment.employeeId} not found",
        )
        ensure_resource_exists(
            connection,
            "employees",
            new_comment.authorId,
            f"Author employee {new_comment.authorId} not found",
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


@router.delete("/{comment_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int):
    """Delete a comment."""
    with db.engine.begin() as connection:
        ensure_resource_exists(
            connection, 
            "comments", 
            comment_id, 
            "Comment not found"
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM comments
                WHERE id = :comment_id
                """
            ),
            {"comment_id": comment_id},
        )
