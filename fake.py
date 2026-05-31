import sqlalchemy
import os
import dotenv
from faker import Faker
from queue import *
import numpy as np

class Company:
    def __init__(self, name, industry, headquarters, founded_date, active, employees, comments, appraisals, prs):
        self.name = name
        self.industry = industry
        self.headquarters = headquarters
        self.founded_date = founded_date
        self.active = active
        self.employees = employees
        self.comments = comments
        self.appraisals = appraisals
        self.prs = prs

class Employee:
    def __init__(self, company, first, last, email, phone, title_id, level, department, hire_date, current_employee):

        self.company = company
        self.first = first
        self.last = last
        self.email = email
        self.phone = phone
        self.title_id = title_id
        self.level = level
        self.department = department
        self.hire_date = hire_date
        self.current_employee = current_employee

class Comment:
    def __init__(self, employee_id, commenter_id, content, created_at):
        self.employee_id = employee_id
        self.commenter_id = commenter_id
        self.content = content
        self.created_at = created_at

class Appraisal:
    def __init__(self, employee_id, comment, created_at):
        self.employee_id = employee_id
        self.comment = comment
        self.created_at = created_at

class PerformanceReview:
    def __init__(
        self,
        employee_id,
        review_period_start,
        review_period_end,
        review_date,
        reviewer_id,
        overall_rating,
        category_1,
        category_2,
        category_3,
        comment,
        title_change,
        level_change,
    ):
        self.employee_id = employee_id
        self.review_period_start = review_period_start
        self.review_period_end = review_period_end
        self.review_date = review_date
        self.reviewer_id = reviewer_id
        self.overall_rating = overall_rating
        self.category_1 = category_1
        self.category_2 = category_2
        self.category_3 = category_3
        self.comment = comment
        self.title_change = title_change
        self.level_change = level_change

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

def create_small_company():
    # generate name, industry, headquarters, founded_date, active
    name = 'placeholder'
    # randomly generate so 50% have founded date as null
    # maybe have all have founded_date as null since it would be hard to sync that up with
    #   the hire dates/prs of employees and i dont think it rlly matters to any of our queries
    #   or just make it like 100 years ago
    # randomly make 5% of companies inactive

    employees = []
    levels = 2
    employees_per_level = 5
    # generate employees:
    # generate CEO (using faker)
    # CEO department = 'ALL'
    # append to list
    make_suboordinate_queue = Queue()
    for i in range(employees_per_level):
        # generate an employee using faker
        # add to make_suboordinate_queue
        pass
    while not make_suboordinate_queue.empty():
        # pop the top person
        # get their department
        # generate employee and add to list
        pass

    pass

# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)
titles = ['CEO', 'Manager', 'Grunt']
# TODO
departments = []
headquarters = []

with engine.begin() as conn:
    # truncate tables
    conn.execute(sqlalchemy.text("""
    """))

    # insert all 3 titles into titles w/ known ids
    # create appropriate number of small companies & append info
    # create appropriate number of medium companies & append info
    # create appropriate number of large companies & append info
    # insert all