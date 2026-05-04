from fastapi import FastAPI

from src.api.routes import companies, employees


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Performance Reviews API"}


app.include_router(companies.router)
app.include_router(employees.router)
