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
    prefix="/title",
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
        ).one_or_none()

    if title is None:
        raise HTTPException(status_code=404, detail="Title not found")

    return Title(id=title.id, name=title.name)


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
        )
        all_titles = [Title(id=t.id, name=t.name) for t in titles]
    return all_titles


@router.post("/", response_model=Title)
def add_title(new_title: NewTitle):
    with db.engine.begin() as connection:
        new_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO titles
                (name)
                VALUES
                (:name)
                RETURNING id
                """
            ),
            {"name": new_title.name},
        ).scalar_one()

    return Title(id=new_id, name=new_title.name)


@router.delete("/{title_id}/", response_model=Title)
def delete_title(title_id: int):
    with db.engine.begin() as connection:
        deleted = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM titles
                WHERE id = :title_id
                RETURNING
                name
                """
            ),
            {"title_id": title_id},
        ).one_or_none()

    if deleted is None:
        raise HTTPException(status_code=404, detail="Title not found")

    return Title(id=title_id, name=deleted.name)
