from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, Depends
import sqlalchemy
from pydantic import BaseModel, Field

from src.api import db
from src.api.routes import auth
from src.api.routes.helpers import ensure_resource_exists


class Employee(BaseModel):
    id: int
    company_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    title_id: int
    level: int  # should probably make this annotated
    department: str
    hire_date: date
    current_employee: bool


class NewEmployee(BaseModel):
    company_id: int
    first_name: str
    last_name: str
    email: str
    phone: str = Field(min_length=10, max_length=10)
    title_id: int
    level: int  # should probably make this annotated
    department: str
    hire_date: date
    current_employee: bool


class EmployeeStats(BaseModel):
    employee_id: int
    company_id: int
    first_name: str
    last_name: str
    department: str
    start_date: Optional[date] = None
    end_date: date
    total_reviews: int
    average_category_1: Optional[float] = None
    average_category_2: Optional[float] = None
    average_category_3: Optional[float] = None
    title_change_count: int
    title_change_rate: float
    level_change_count: int
    level_change_rate: float


router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.get("/{employee_id}/", response_model=Employee)
def get_employee(employee_id: int):
    """Get one employee by id."""
    with db.engine.begin() as connection:
        employee = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, company_id, first_name, last_name,
                    email, phone, title_id, level, department,
                    hire_date, current_employee
                FROM employees
                WHERE id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        ).mappings().one_or_none()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return dict(employee)


@router.get(
    "/{employee_id}/stats/",
    response_model=EmployeeStats,
)
def get_employee_stats(
    employee_id: int,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
):
    """Get review stats for one employee."""
    with db.engine.begin() as connection:
        employee = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, company_id, first_name, last_name,
                    department, hire_date
                FROM employees
                WHERE id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        ).mappings().one_or_none()

        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        effective_start_date = start_date or employee["hire_date"]
        effective_end_date = end_date or date.today()

        if (
            effective_start_date is not None
            and effective_start_date > effective_end_date
        ):
            raise HTTPException(
                status_code=400,
                detail="start_date must be on or before end_date",
            )

        stats = (
            connection.execute(
                sqlalchemy.text(
                    """
                SELECT
                    COUNT(id) AS total_reviews,
                    AVG(category_1) AS average_category_1,
                    AVG(category_2) AS average_category_2,
                    AVG(category_3) AS average_category_3,
                    COUNT(*) FILTER (
                        WHERE title_change = 1
                    ) AS title_change_count,
                    COUNT(*) FILTER (
                        WHERE level_change = 1
                    ) AS level_change_count
                FROM performance_reviews
                WHERE employee_id = :employee_id
                    AND (:start_date IS NULL OR review_date >= :start_date)
                    AND (:end_date IS NULL OR review_date <= :end_date)
                """
                ),
                {
                    "employee_id": employee_id,
                    "start_date": effective_start_date,
                    "end_date": effective_end_date,
                },
            )
            .mappings()
            .one()
        )

    total_reviews = stats["total_reviews"]
    title_change_count = stats["title_change_count"]
    level_change_count = stats["level_change_count"]

    return EmployeeStats(
        employee_id=employee["id"],
        company_id=employee["company_id"],
        first_name=employee["first_name"],
        last_name=employee["last_name"],
        department=employee["department"],
        start_date=effective_start_date,
        end_date=effective_end_date,
        total_reviews=total_reviews,
        average_category_1=stats["average_category_1"],
        average_category_2=stats["average_category_2"],
        average_category_3=stats["average_category_3"],
        title_change_count=title_change_count,
        title_change_rate=(title_change_count / total_reviews * 100) if total_reviews > 0 else 0,
        level_change_count=level_change_count,
        level_change_rate=(level_change_count / total_reviews * 100) if total_reviews > 0 else 0,
    )


@router.get(
    "/company/{company_id}/", response_model=List[Employee]
)
def get_employees(company_id: int) -> List[Employee]:
    """Get employees for one company."""
    with db.engine.begin() as connection:
        employees = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, company_id, first_name, last_name, email, phone, title_id, level, department, hire_date, current_employee
                FROM employees
                WHERE company_id = :company_id
                """
            ),
            {"company_id": company_id},
        ).mappings().all()
        all_employees = [dict(e) for e in employees]
    return all_employees


@router.post("/", response_model=Employee, status_code=201)
def add_employee(new_employee: NewEmployee):
    """Create an employee."""
    with db.engine.begin() as connection:
        ensure_resource_exists(
            connection,
            "companies",
            new_employee.company_id,
            "Company not found"
        )
        ensure_resource_exists(
            connection,
            "titles",
            new_employee.title_id,
            "Title not found"
        )

        employee = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO employees
                (company_id, first_name, last_name, email, phone, title_id, level, department, hire_date, current_employee)
                VALUES
                (:company_id, :first_name, :last_name, :email, :phone, :title_id, :level, :department, :hire_date, :current_employee)
                RETURNING id, company_id, first_name, last_name, email, phone,
                    title_id, level, department, hire_date, current_employee
                """
            ),
            {
                "company_id": new_employee.company_id,
                "first_name": new_employee.first_name,
                "last_name": new_employee.last_name,
                "phone": new_employee.phone,
                "email": new_employee.email,
                "title_id": new_employee.title_id,
                "level": new_employee.level,
                "department": new_employee.department,
                "hire_date": new_employee.hire_date,
                "current_employee": new_employee.current_employee,
            },
        ).mappings().one()

    return dict(employee)


@router.delete("/{employee_id}/", status_code=204)
def delete_employee(employee_id: int):
    """Delete an employee."""
    with db.engine.begin() as connection:
        ensure_resource_exists(
            connection,
            "employees",
            employee_id,
            "Employee not found"
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM comments
                WHERE employee_id = :employee_id
                    OR commenter_id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM performance_reviews
                WHERE employee_id = :employee_id
                    OR reviewer_id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM appraisals
                WHERE employee_id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        )

        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM employees
                WHERE id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        )

