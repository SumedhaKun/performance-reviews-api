from fastapi import APIRouter, HTTPException

from src.api.db import get_connection

router = APIRouter()


@router.get("/employees/{employee_id}")
def get_employee(employee_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, company_id, first_name, last_name,
            email, phone, title_id, level, department,
            hire_date, current_employee
        FROM employees
        WHERE id = %s
        """,
        (employee_id,),
    )

    employee = cursor.fetchone()

    cursor.close()
    connection.close()

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee
