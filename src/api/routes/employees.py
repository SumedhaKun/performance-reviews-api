from datetime import date
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
import sqlalchemy
from pydantic import BaseModel

from src.api import db

router = APIRouter()

class Employee(BaseModel):
    id: int
    company_id: int
    first_name: str
    last_name: str
    email: str
    phone: int
    title_id: int
    level: int # should probably make this annotated
    department: str
    hire_date: str
    current_employee: bool

class NewEmployee(BaseModel):
    company_id: int
    first_name: str
    last_name: str
    email: str
    phone: int
    title_id: int
    level: int # should probably make this annotated
    department: str
    hire_date: str
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


@router.get("/employees/{employee_id}", tags=["employees"], response_model=Employee)
def get_employee(employee_id: int):
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
        ).one_or_none()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return Employee(
        id = employee_id,
        company_id = employee.company_id,
        first_name = employee.first_name,
        last_name = employee.last_name,
        email = employee.email,
        phone = employee.phone,
        title_id = employee.title_id,
        level = employee.level,
        department = employee.department,
        hire_date = str(employee.hire_date),
        current_employee = employee.current_employee
    )


@router.get(
    "/employees/{employee_id}/stats",
    tags=["employees"],
    response_model=EmployeeStats,
)
def get_employee_stats(
    employee_id: int,
    start_date: Optional[date] = Query(default=None),
    end_date: Optional[date] = Query(default=None),
):
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
        ).one_or_none()

        if employee is None:
            raise HTTPException(status_code=404, detail="Employee not found")

        effective_start_date = start_date or employee.hire_date
        effective_end_date = end_date or date.today()

        if (
            effective_start_date is not None
            and effective_start_date > effective_end_date
        ):
            raise HTTPException(
                status_code=400,
                detail="start_date must be on or before end_date",
            )

        stats = connection.execute(
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
        ).mappings().one()

    total_reviews = stats["total_reviews"]
    title_change_count = stats["title_change_count"]
    level_change_count = stats["level_change_count"]

    return EmployeeStats(
        employee_id=employee.id,
        company_id=employee.company_id,
        first_name=employee.first_name,
        last_name=employee.last_name,
        department=employee.department,
        start_date=effective_start_date,
        end_date=effective_end_date,
        total_reviews=total_reviews,
        average_category_1=stats["average_category_1"],
        average_category_2=stats["average_category_2"],
        average_category_3=stats["average_category_3"],
        title_change_count=title_change_count,
        title_change_rate=(
            title_change_count / total_reviews * 100
        ),
        level_change_count=level_change_count,
        level_change_rate=(
            level_change_count / total_reviews * 100
        ),
    )

@router.get("/employees/company/{company_id}", tags=["employees"], response_model=List[Employee])
def get_employees(company_id: int) -> List[Employee]:
    """
    Retrieves all employees
    """
    with db.engine.begin() as connection:
        employees = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, company_id, first_name, last_name, email, phone, title_id, level, department, hire_date, current_employee
                FROM employees
                WHERE company_id = :cid
                """
            ),
            [{"cid": company_id}]
        )
        all_employees = [
            Employee(
                id = e.id,
                company_id = e.company_id,
                first_name = e.first_name,
                last_name = e.last_name,
                email = e.email,
                phone = e.phone,
                title_id = e.title_id,
                level = e.level,
                department = e.department,
                hire_date = str(e.hire_date),
                current_employee = e.current_employee
            )
            for e in employees
        ]
    return all_employees

@router.post("/employees/", tags=["employees"], response_model=Employee)
def add_employee(new_employee: NewEmployee):
    with db.engine.begin() as connection:
        new_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO employees
                (company_id, first_name, last_name, email, phone, title_id, level, department, hire_date, current_employee)
                VALUES
                (:cid, :fn, :ln, :email, :phone, :tid, :level, :dep, :hire_date, :curr_emp)
                RETURNING id
                """
            ),
            [{
                "cid": new_employee.company_id,
                "fn": new_employee.first_name,
                "ln": new_employee.last_name,
                "phone": new_employee.phone,
                "email": new_employee.email,
                "tid": new_employee.title_id,
                "level": new_employee.level,
                "dep": new_employee.department,
                "hire_date": new_employee.hire_date,
                "curr_emp": new_employee.current_employee
            }]
        ).scalar_one()

    return Employee(
        id = new_id,
        company_id = new_employee.company_id,
        first_name = new_employee.first_name,
        last_name = new_employee.last_name,
        email = new_employee.email,
        phone = new_employee.phone,
        title_id = new_employee.title_id,
        level = new_employee.level,
        department = new_employee.department,
        hire_date = new_employee.hire_date,
        current_employee = new_employee.current_employee
    )

@router.delete("/employees/{employee_id}/", tags=["employees"], response_model=Employee)
def delete_employee(employee_id: int):
    with db.engine.begin() as connection:
        deleted = connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM employees
                WHERE id = :eid
                RETURNING
                company_id, first_name, last_name, email, phone, title_id, level, department, hire_date, current_employee
                """
            ),
            [{"eid": employee_id}]
        ).one_or_none()
    
    if deleted is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return Employee(
        id = employee_id,
        company_id = deleted.company_id,
        first_name = deleted.first_name,
        last_name = deleted.last_name,
        email = deleted.email,
        phone = deleted.phone,
        title_id = deleted.title_id,
        level = deleted.level,
        department = deleted.department,
        hire_date = str(deleted.hire_date),
        current_employee = deleted.current_employee
    )