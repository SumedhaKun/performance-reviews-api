from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Depends, status
from pydantic import BaseModel
import sqlalchemy

from src.api import db
from src.api.routes import auth


class NewCompany(BaseModel):
    name: str
    industry: str
    headquarters_location: str
    founded_date: Optional[date] = None
    active: bool = True


class Company(BaseModel):
    id: int
    name: str
    industry: str
    headquarters_location: str
    founded_date: Optional[date] = None
    active: bool


class DepartmentStats(BaseModel):
    company_id: int
    department: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    employee_count: int
    total_reviews: int
    average_category_1: Optional[float] = None
    average_category_2: Optional[float] = None
    average_category_3: Optional[float] = None
    title_change_count: int
    title_change_rate: float
    level_change_count: int
    level_change_rate: float

router = APIRouter(
    prefix="/companies",
    tags=["companies"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/{company_id}/", response_model=Company, status_code=status.HTTP_200_OK)
def get_company(company_id: int):
    """Get one company by id."""
    with db.engine.begin() as connection:
        company = (
            connection.execute(
                sqlalchemy.text(
                    """
                SELECT id, name, industry,
                    headquarters_location, founded_date, active
                FROM companies
                WHERE id = :company_id
                """
                ),
                {"company_id": company_id},
            )
            .mappings()
            .one_or_none()
        )

    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    return dict(company)


@router.get(
    "/{company_id}/departments/{department}/stats/",
    response_model=DepartmentStats, status_code=status.HTTP_200_OK
)
def get_department_stats(
    company_id: int,
    department: str,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
):
    """Get review stats for one company department."""
    with db.engine.begin() as connection:
        company = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, founded_date
                FROM companies
                WHERE id = :company_id
                """
            ),
            {"company_id": company_id},
        ).one_or_none()

        if company is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

        departments = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1
                FROM employees
                WHERE company_id = :company_id AND department = :department
                LIMIT 1
                """
            ),
            {"company_id": company_id, "department": department},
        ).one_or_none()

        if departments is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")


        earliest_hire_date = connection.execute(
            sqlalchemy.text(
                """
                SELECT MIN(hire_date)
                FROM employees
                WHERE company_id = :company_id
                    AND department = :department
                """
            ),
            {
                "company_id": company_id,
                "department": department,
            },
        ).scalar_one()

        effective_start_date = start_date or company.founded_date or earliest_hire_date
        effective_end_date = end_date or date.today()

        if (
            effective_start_date is not None
            and effective_start_date > effective_end_date
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be on or before end_date",
            )

        stats = (
            connection.execute(
                sqlalchemy.text(
                    """
                WITH department_employees AS (
                    SELECT id
                    FROM employees
                    WHERE company_id = :company_id
                        AND department = :department
                )
                SELECT
                    COUNT(DISTINCT de.id) AS employee_count,
                    COUNT(pr.id) AS total_reviews,
                    AVG(pr.category_1) AS average_category_1,
                    AVG(pr.category_2) AS average_category_2,
                    AVG(pr.category_3) AS average_category_3,
                    COUNT(*) FILTER (
                        WHERE pr.title_change = 1
                    ) AS title_change_count,
                    COUNT(*) FILTER (
                        WHERE pr.level_change = 1
                    ) AS level_change_count
                FROM department_employees de
                LEFT JOIN performance_reviews pr
                    ON pr.employee_id = de.id
                    AND (:start_date IS NULL OR pr.review_date >= :start_date)
                    AND (:end_date IS NULL OR pr.review_date <= :end_date)
                """
                ),
                {
                    "company_id": company_id,
                    "department": department,
                    "start_date": effective_start_date,
                    "end_date": effective_end_date,
                },
            )
            .mappings()
            .one()
        )

    if stats["employee_count"] == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    total_reviews = stats["total_reviews"]
    title_change_count = stats["title_change_count"]
    level_change_count = stats["level_change_count"]

    return DepartmentStats(
        company_id=company_id,
        department=department,
        start_date=effective_start_date,
        end_date=effective_end_date,
        employee_count=stats["employee_count"],
        total_reviews=total_reviews,
        average_category_1=stats["average_category_1"],
        average_category_2=stats["average_category_2"],
        average_category_3=stats["average_category_3"],
        title_change_count=title_change_count,
        title_change_rate= (title_change_count / total_reviews * 100) if total_reviews > 0 else 0,
        level_change_count=level_change_count,
        level_change_rate=(level_change_count / total_reviews * 100) if total_reviews > 0 else 0,
    )


@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
def create_company(new_company: NewCompany):
    """Create a company."""
    with db.engine.begin() as connection:
        company = (
            connection.execute(
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
            )
            .mappings()
            .one()
        )

    return dict(company)
