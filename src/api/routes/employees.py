from fastapi import APIRouter, HTTPException
import sqlalchemy

from src.api import db

router = APIRouter()


@router.get("/employees/{employee_id}")
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
        ).mappings().one_or_none()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return dict(employee)
