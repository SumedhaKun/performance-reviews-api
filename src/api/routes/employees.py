from fastapi import APIRouter, HTTPException
import sqlalchemy
from pydantic import BaseModel
from typing import List

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