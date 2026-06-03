from fastapi import APIRouter, HTTPException, Depends, status
import sqlalchemy
from pydantic import BaseModel
from typing import List

from src.api import db
from src.api.routes import auth
from src.api.routes.helpers import ensure_resource_exists


class Title(BaseModel):
    id: int
    name: str


class NewTitle(BaseModel):
    name: str

router = APIRouter(
    prefix="/titles",
    tags=["titles"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/{title_id}/", response_model=Title, status_code=status.HTTP_200_OK)
def get_title(title_id: int):
    """Get one title by id."""
    with db.engine.begin() as connection:
        title = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name
                FROM titles
                WHERE id = :title_id
                """
            ),
            {"title_id": title_id},
        ).mappings().one_or_none()

    if title is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Title not found")

    return dict(title)


@router.get("/", response_model=List[Title], status_code=status.HTTP_200_OK)
def get_titles() -> List[Title]:
    """Get all titles."""
    with db.engine.begin() as connection:
        titles = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name
                FROM titles
                """
            )
        ).mappings().all()

    all_titles = [dict(title) for title in titles]
    return all_titles


@router.post("/", response_model=Title, status_code=status.HTTP_201_CREATED)
def add_title(new_title: NewTitle):
    """Create a title."""
    with db.engine.begin() as connection:
        title = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO titles
                (name)
                VALUES
                (:name)
                RETURNING id, name
                """
            ),
            {"name": new_title.name},
        ).mappings().one()

    return dict(title)


@router.delete("/{title_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_title(title_id: int):
    """Delete a title."""
    with db.engine.begin() as connection:
        ensure_resource_exists(
            connection, 
            "titles", 
            title_id, 
            "Title not found"
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM titles
                WHERE id = :title_id
                """
            ),
            {"title_id": title_id},
        )
