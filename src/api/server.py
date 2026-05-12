from fastapi import FastAPI

from src.api.routes import comments, companies, employees, performance_reviews, titles


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Performance Reviews API"}


app.include_router(companies.router)
app.include_router(comments.router)
app.include_router(employees.router)
app.include_router(performance_reviews.router)
app.include_router(titles.router)
