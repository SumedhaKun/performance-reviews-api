from fastapi import HTTPException, status
import sqlalchemy


VALID_RESOURCE_TABLES = {
    "comments",
    "companies",
    "employees",
    "performance_reviews",
    "titles",
}


def ensure_resource_exists(connection, table_name: str, resource_id: int, detail: str):
    if table_name not in VALID_RESOURCE_TABLES:
        raise ValueError(f"Unsupported resource table: {table_name}")

    resource_exists = connection.execute(
        sqlalchemy.text(f"""
            SELECT 1
            FROM {table_name}
            WHERE id = :resource_id
        """),
        {"resource_id": resource_id},
    ).one_or_none()

    if resource_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def format_comment(comment):
    return {
        "id": comment["id"],
        "employeeId": comment["employee_id"],
        "subject": comment["subject"],
        "comment": comment["content"],
        "authorId": comment["commenter_id"],
        "createdAt": comment["created_at"],
    }
