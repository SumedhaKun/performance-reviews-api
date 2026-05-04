from fastapi import APIRouter, HTTPException

from src.api.db import get_connection


router = APIRouter()


@router.get("/companies/{company_id}")
def get_company(company_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, industry, 
        headquarters_location, founded_date, active
        FROM companies
        WHERE id = %s
        """,
        (company_id,),
    )

    company = cursor.fetchone()

    cursor.close()
    connection.close()

    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    return company
