from fastapi import APIRouter, HTTPException, Depends
import sqlalchemy
from pydantic import BaseModel
from typing import List

from src.api import db
from src.api.routes import auth


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


@router.get("/{title_id}")
def get_tag(title_id: int):
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
        raise HTTPException(status_code=404, detail="Title not found")

    return dict(title)


@router.get("/", response_model=List[Title])
def get_titles() -> List[Title]:
    """
    Retrieves all titles
    """
    with db.engine.begin() as connection:
        titles = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name
                FROM titles
                """
            )
        ).mappings().all()
        all_titles = [dict(title) for t in titles]
    return all_titles


@router.post("/", response_model=Title)
def add_title(new_title: NewTitle):
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


@router.delete("/{title_id}/", status_code=204)
def delete_title(title_id: int):
    with db.engine.begin() as connection:
        title_exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM titles
                WHERE id = :title_id
                """
            ),
            {"title_id": title_id},
        ).one_or_none()

        if title_exists is None:
            raise HTTPException(status_code=404, detail="Title not found")

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM titles
                WHERE id = :title_id
                """
            ),
            {"title_id": title_id},
        )
