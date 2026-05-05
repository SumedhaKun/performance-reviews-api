from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlalchemy

from src.api import db


router = APIRouter()


class NewCompany(BaseModel):
    name: str
    industry: str
    headquarters_location: str
    founded_date: Optional[date] = None
    active: bool = True


@router.get("/companies/{company_id}")
def get_company(company_id: int):
    with db.engine.begin() as connection:
        company = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name, industry,
                    headquarters_location, founded_date, active
                FROM companies
                WHERE id = :company_id
                """
            ),
            {"company_id": company_id},
        ).mappings().one_or_none()

    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return dict(company)


@router.post("/companies", status_code=201)
def create_company(new_company: NewCompany):
    with db.engine.begin() as connection:
        company = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO companies (
                    name,
                    industry,
                    headquarters_location,
                    founded_date,
                    active
                )
                VALUES (
                    :name,
                    :industry,
                    :headquarters_location,
                    :founded_date,
                    :active
                )
                RETURNING id, name, industry,
                    headquarters_location, founded_date, active
                """
            ),
            {
                "name": new_company.name,
                "industry": new_company.industry,
                "headquarters_location": new_company.headquarters_location,
                "founded_date": new_company.founded_date,
                "active": new_company.active,
            },
        ).mappings().one()

    return dict(company)
