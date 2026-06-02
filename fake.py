import sqlalchemy
#import os
#import dotenv
from faker import Faker
import random
from queue import *
from datetime import date, datetime
import numpy as np


'''
CALCULATIONS:
DATA GENERATION TARGETS

Company counts:
- 60 mini companies   × 60 employees   = 3,600
- 122 small companies × 200 employees  = 24,400
- 16 medium companies × 2,000 employees = 32,000
- 6 large companies   × 10,000 employees = 60,000

Total employees: 120,000

Each employee receives:
- Employee record
- ~20 comments
- One appraisal per eligible year
- One performance review per eligible year

'''
mini_companies = 60
small_companies = 122
medium_companies = 16
large_companies = 6

class Company:
    def __init__(self, name, industry, headquarters, active):
        self.name = name
        self.industry = industry
        self.headquarters = headquarters
        self.active = active

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
    def __init__(self, employee_id, commenter_id, content, created_at, subject):
        self.employee_id = employee_id
        self.commenter_id = commenter_id
        self.content = content
        self.created_at = created_at
        self.subject = subject

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
    #dotenv.load_dotenv()
    #DB_USER: str = os.environ.get("POSTGRES_USER")
    #DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    #DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    #DB_PORT: str = os.environ.get("POSTGRES_PORT")
    #DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql+psycopg://myuser:mypassword@localhost/pr_database"

def fake_employee():
    first = fake.first_name()
    last = fake.last_name()

    return Employee(
        company=None,  # unknown for now
        first=first,
        last=last,
        email=fake.email(),
        phone=fake.phone_number(),
        title_id=None,  # generated later
        level=None,     # generated later
        department=random.choice(departments),
        hire_date=fake.date_between(start_date="-30y", end_date="today"),
        current_employee=random.random() >= 0.08,  # 8% inactive
    )



# Create a new DB engine based on our connection string
engine = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)
fake = Faker()
rng = np.random.default_rng()
titles = ['CEO', 'Manager', 'Grunt']
departments = ['IT', 'HR', 'Sales', 'Customer Service', 'Product Development']
industries = ['Tech', 'Finance', 'Education', 'Social', 'Fashion']
headquarters = ['SLO', 'LA', 'NY', 'SF', 'Santa Maria']
subjects = ['Work ethic', 'Efficiency', 'Punctuality', 'Other', 'Teamwork', 'Leadership', 'Improvement']
mini_company_employees = 60
small_company_employees = 200
medium_company_employees = 2000
large_company_employees = 10000
comments_per_employee = 20

with engine.begin() as conn:
    # truncate tables
    conn.execute(
        sqlalchemy.text(
            """
            TRUNCATE TABLE titles RESTART IDENTITY CASCADE;
            TRUNCATE TABLE employees RESTART IDENTITY CASCADE;
            TRUNCATE TABLE companies RESTART IDENTITY CASCADE;
            TRUNCATE TABLE appraisals;
            TRUNCATE TABLE comments;
            TRUNCATE TABLE performance_reviews;
            """
        )
    )

    conn.execute(
        sqlalchemy.text(
            """
            INSERT INTO titles (name) VALUES (:t)
            """
        ), [{'t': title} for title in titles]
    )

    num_employees = (mini_companies * mini_company_employees +
    small_companies * small_company_employees +
    medium_companies * medium_company_employees +
    large_companies * large_company_employees)
    employees = [fake_employee() for _ in range(num_employees)]
    print('employees generated')
    companies = []
    comments = []
    appraisals = []
    prs = []

    employee_offset = 0
    company_id = 1
    # make mini companies
    for _ in range(mini_companies):
        # make company
        print(f'company {company_id}, employee {employee_offset}')
        appraisal_month = random.randint(1, 12)
        appraisal_day = random.randint(1, 28)
        companies.append(
            Company(
                fake.company(),
                random.choice(industries),
                random.choice(headquarters),
                random.random() >= 0.05
            )
        )

        # for each employee
        for i in range(employee_offset, employee_offset + mini_company_employees):
            employees[i].company = company_id
            for _ in range(comments_per_employee):
                comments.append(
                    Comment(
                        employee_id=i + 1,
                        commenter_id=random.randint(employee_offset, employee_offset + mini_company_employees - 1) + 1,
                        content=fake.paragraph(nb_sentences=1),
                        created_at=fake.date_time_between(
                            start_date=employees[i].hire_date,
                            end_date="now"
                        ),
                        subject=random.choice(subjects)
                    )
                )
            # make one appraisal per year that the employee has been hired
            for year in range(employees[i].hire_date.year, 2026 + 1):
                appraisal_date = date(year, appraisal_month, appraisal_day)

                # Skip June 13 of hire year if they were hired after June 13
                if appraisal_date < employees[i].hire_date:
                    continue

                appraisals.append(
                    Appraisal(
                        employee_id=i + 1,
                        comment=fake.paragraph(nb_sentences=3),
                        created_at=datetime(year, appraisal_month, appraisal_day)
                    )
                )
            # make one performance review per year that the employee has been hired
            for year in range(employees[i].hire_date.year, 2026):
                review_date = date(year, appraisal_month, appraisal_day)
                if appraisal_date < employees[i].hire_date:
                    continue

                ratings = rng.normal(7, 1, 4)
                prs.append(
                    PerformanceReview(
                        employee_id = i + 1,
                        review_period_start = date(year, 1, 1),
                        review_period_end = date(year, 12, 31),
                        review_date = review_date,
                        reviewer_id = random.randint(employee_offset + 1, employee_offset + 4),
                        overall_rating = ratings[0],
                        category_1 = ratings[1],
                        category_2 = ratings[2],
                        category_3 = ratings[3],
                        comment = fake.paragraph(nb_sentences=1),
                        title_change = int(random.random() <= 0.05),
                        level_change = int(random.random() <= 0.05)
                    )
                )
        # make ceo
        employees[employee_offset].title_id = 1
        employees[employee_offset].department = 'All'
        employees[employee_offset].active = True
        employees[employee_offset].level = 1

        # make managers
        for i in range(employee_offset + 1, employee_offset + 4):
            employees[i].title_id = 2
            employees[i].level = 2
        # make regular employees
        for i in range(employee_offset + 4, employee_offset + mini_company_employees):
            employees[i].title_id = 3
            employees[i].level = 3

        company_id += 1
        employee_offset += mini_company_employees



    # make small companies
    for _ in range(small_companies):
        # make company
        print(f'company {company_id}, employee {employee_offset}')
        appraisal_month = random.randint(1, 12)
        appraisal_day = random.randint(1, 28)
        # levels = 4
        last_manager = employee_offset + (small_company_employees // 3)

        companies.append(
            Company(
                fake.company(),
                random.choice(industries),
                random.choice(headquarters),
                random.random() >= 0.05
            )
        )

        # for each employee
        for i in range(employee_offset, employee_offset + small_company_employees):
            employees[i].company = company_id
            for _ in range(comments_per_employee):
                comments.append(
                    Comment(
                        employee_id=i + 1,
                        commenter_id=random.randint(employee_offset, employee_offset + small_company_employees - 1) + 1,
                        content=fake.paragraph(nb_sentences=1),
                        created_at=fake.date_time_between(
                            start_date=employees[i].hire_date,
                            end_date="now"
                        ),
                        subject=random.choice(subjects)
                    )
                )
            # make one appraisal per year that the employee has been hired
            for year in range(employees[i].hire_date.year, 2026 + 1):
                appraisal_date = date(year, appraisal_month, appraisal_day)

                # Skip June 13 of hire year if they were hired after June 13
                if appraisal_date < employees[i].hire_date:
                    continue

                appraisals.append(
                    Appraisal(
                        employee_id=i + 1,
                        comment=fake.paragraph(nb_sentences=3),
                        created_at=datetime(year, appraisal_month, appraisal_day)
                    )
                )
            # make one performance review per year that the employee has been hired
            for year in range(employees[i].hire_date.year, 2026):
                review_date = date(year, appraisal_month, appraisal_day)
                if appraisal_date < employees[i].hire_date:
                    continue

                ratings = rng.normal(7, 1, 4)
                prs.append(
                    PerformanceReview(
                        employee_id = i + 1,
                        review_period_start = date(year, 1, 1),
                        review_period_end = date(year, 12, 31),
                        review_date = review_date,
                        reviewer_id = random.randint(employee_offset, last_manager) + 1,
                        overall_rating = ratings[0],
                        category_1 = ratings[1],
                        category_2 = ratings[2],
                        category_3 = ratings[3],
                        comment = fake.paragraph(nb_sentences=1),
                        title_change = int(random.random() <= 0.05),
                        level_change = int(random.random() <= 0.05)
                    )
                )
        # make ceo
        employees[employee_offset].title_id = 1
        employees[employee_offset].department = 'All'
        employees[employee_offset].active = True
        employees[employee_offset].level = 1

        # make managers
        for i in range(employee_offset + 1, last_manager + 1):
            employees[i].title_id = 2
            employees[i].level = random.randint(2, 3)
        # make regular employees

        for i in range(last_manager + 1, employee_offset + small_company_employees):
            employees[i].title_id = 3
            employees[i].level = 4

        company_id += 1
        employee_offset += small_company_employees

    # make medium companies
    for _ in range(medium_companies):
        # make company
        print(f'company {company_id}, employee {employee_offset}')
        appraisal_month = random.randint(1, 12)
        appraisal_day = random.randint(1, 28)
        levels = random.randint(7, 12)
        last_manager = employee_offset + (medium_company_employees // 2)

        companies.append(
            Company(
                fake.company(),
                random.choice(industries),
                random.choice(headquarters),
                random.random() >= 0.05
            )
        )

        # for each employee
        for i in range(employee_offset, employee_offset + medium_company_employees):
            employees[i].company = company_id
            for _ in range(comments_per_employee):
                comments.append(
                    Comment(
                        employee_id=i + 1,
                        commenter_id=random.randint(employee_offset, employee_offset + medium_company_employees - 1) + 1,
                        content=fake.paragraph(nb_sentences=1),
                        created_at=fake.date_time_between(
                            start_date=employees[i].hire_date,
                            end_date="now"
                        ),
                        subject=random.choice(subjects)
                    )
                )
            # make one appraisal per year that the employee has been hired
            for year in range(employees[i].hire_date.year, 2026 + 1):
                appraisal_date = date(year, appraisal_month, appraisal_day)

                # Skip June 13 of hire year if they were hired after June 13
                if appraisal_date < employees[i].hire_date:
                    continue

                appraisals.append(
                    Appraisal(
                        employee_id=i + 1,
                        comment=fake.paragraph(nb_sentences=3),
                        created_at=datetime(year, appraisal_month, appraisal_day)
                    )
                )
            # make one performance review per year that the employee has been hired
            for year in range(employees[i].hire_date.year, 2026):
                review_date = date(year, appraisal_month, appraisal_day)
                if appraisal_date < employees[i].hire_date:
                    continue

                ratings = rng.normal(7, 1, 4)
                prs.append(
                    PerformanceReview(
                        employee_id = i + 1,
                        review_period_start = date(year, 1, 1),
                        review_period_end = date(year, 12, 31),
                        review_date = review_date,
                        reviewer_id = random.randint(employee_offset, last_manager) + 1,
                        overall_rating = ratings[0],
                        category_1 = ratings[1],
                        category_2 = ratings[2],
                        category_3 = ratings[3],
                        comment = fake.paragraph(nb_sentences=1),
                        title_change = int(random.random() <= 0.05),
                        level_change = int(random.random() <= 0.05)
                    )
                )
        # make ceo
        employees[employee_offset].title_id = 1
        employees[employee_offset].department = 'All'
        employees[employee_offset].active = True
        employees[employee_offset].level = 1

        # make managers
        for i in range(employee_offset + 1, last_manager + 1):
            employees[i].title_id = 2
            employees[i].level = random.randint(2, levels - 1)
        # make regular employees

        for i in range(last_manager + 1, employee_offset + medium_company_employees):
            employees[i].title_id = 3
            employees[i].level = random.randint(levels // 2 + 1, levels)

        company_id += 1
        employee_offset += medium_company_employees

    # make large companies
    for _ in range(large_companies):
        # make company
        print(f'company {company_id}, employee {employee_offset}')
        appraisal_month = random.randint(1, 12)
        appraisal_day = random.randint(1, 28)
        levels = random.randint(15, 20)
        last_manager = employee_offset + int(large_company_employees * 0.65)

        companies.append(
            Company(
                fake.company(),
                random.choice(industries),
                random.choice(headquarters),
                random.random() >= 0.05
            )
        )

        # for each employee
        for i in range(employee_offset, employee_offset + large_company_employees):
            employees[i].company = company_id
            for _ in range(comments_per_employee):
                comments.append(
                    Comment(
                        employee_id=i + 1,
                        commenter_id=random.randint(employee_offset, employee_offset + large_company_employees - 1) + 1,
                        content=fake.paragraph(nb_sentences=1),
                        created_at=fake.date_time_between(
                            start_date=employees[i].hire_date,
                            end_date="now"
                        ),
                        subject=random.choice(subjects)
                    )
                )
            # make one appraisal per year that the employee has been hired
            for year in range(employees[i].hire_date.year, 2026 + 1):
                appraisal_date = date(year, appraisal_month, appraisal_day)

                # Skip June 13 of hire year if they were hired after June 13
                if appraisal_date < employees[i].hire_date:
                    continue

                appraisals.append(
                    Appraisal(
                        employee_id=i + 1,
                        comment=fake.paragraph(nb_sentences=3),
                        created_at=datetime(year, appraisal_month, appraisal_day)
                    )
                )
            # make one performance review per year that the employee has been hired
            for year in range(employees[i].hire_date.year, 2026):
                review_date = date(year, appraisal_month, appraisal_day)
                if appraisal_date < employees[i].hire_date:
                    continue

                ratings = rng.normal(7, 1, 4)
                prs.append(
                    PerformanceReview(
                        employee_id = i + 1,
                        review_period_start = date(year, 1, 1),
                        review_period_end = date(year, 12, 31),
                        review_date = review_date,
                        reviewer_id = random.randint(employee_offset, last_manager) + 1,
                        overall_rating = ratings[0],
                        category_1 = ratings[1],
                        category_2 = ratings[2],
                        category_3 = ratings[3],
                        comment = fake.paragraph(nb_sentences=1),
                        title_change = int(random.random() <= 0.05),
                        level_change = int(random.random() <= 0.05)
                    )
                )
        # make ceo
        employees[employee_offset].title_id = 1
        employees[employee_offset].department = 'All'
        employees[employee_offset].active = True
        employees[employee_offset].level = 1

        # make managers
        for i in range(employee_offset + 1, last_manager + 1):
            employees[i].title_id = 2
            employees[i].level = random.randint(2, levels - 1)
        # make regular employees

        for i in range(last_manager + 1, employee_offset + large_company_employees):
            employees[i].title_id = 3
            employees[i].level = random.randint(levels // 2 - 7, levels)

        company_id += 1
        employee_offset += large_company_employees

    print("starting insertions")
    conn.execute(
        sqlalchemy.text(
            """
            INSERT INTO companies (name, industry, headquarters_location, active)
            VALUES (:name, :industry, :headquarters, :active)
            """
        ),
        [
            {
                "name": company.name,
                "industry": company.industry,
                "headquarters": company.headquarters,
                "active": company.active,
            }
            for company in companies
        ]
    )
    print("companies inserted")

    conn.execute(
        sqlalchemy.text(
            """
            INSERT INTO employees (company_id, first_name, last_name, email, phone, title_id, level, department, hire_date, current_employee)
            VALUES (:c, :fn, :ln, :email, :phone, :tid, :level, :dep, :hire, :current)
            """
        ),
        [{
            "c": 1 if e.company is None else e.company,
            "fn": e.first,
            "ln": e.last,
            "email": e.email,
            "phone": e.phone,
            "tid": e.title_id,
            "level": e.level,
            "dep": e.department,
            "hire": e.hire_date,
            "current": e.current_employee,
        } for e in employees ]
    )

    print("employees inserted")

    conn.execute(
        sqlalchemy.text(
            """
            INSERT INTO comments (employee_id, commenter_id, content, created_at, subject)
            VALUES (:eid, :cid, :content, :time, :subject)
            """
        ),
        [{"eid": c.employee_id, "cid": c.commenter_id, "content": c.content, "time": c.created_at, "subject": c.subject} for c in comments]
    )

    print("comments inserted")

    conn.execute(
        sqlalchemy.text(
            """
            INSERT INTO appraisals (employee_id, comment, created_at)
            VALUES (:eid, :content, :time)
            """
        ),
        [{"eid": a.employee_id, "content": a.comment, "time": a.created_at} for a in appraisals]
    )

    print("appraisals inserted")

    conn.execute(
        sqlalchemy.text(
            """
            INSERT INTO performance_reviews ( employee_id,
                reviewer_id,
                review_period_start,
                review_period_end,
                review_date,
                overall_rating,
                category_1,
                category_2,
                category_3,
                comment,
                title_change,
                level_change
            )
            VALUES (
                :employee_id,
                :reviewer_id,
                :review_period_start,
                :review_period_end,
                :review_date,
                :overall_rating,
                :category_1,
                :category_2,
                :category_3,
                :comment,
                :title_change,
                :level_change
            )
            """
        ),
        [{
            "employee_id": pr.employee_id,
            "reviewer_id": pr.reviewer_id,
            "review_period_start": pr.review_period_start,
            "review_period_end": pr.review_period_end,
            "review_date": pr.review_date,
            "overall_rating": pr.overall_rating,
            "category_1": pr.category_1,
            "category_2": pr.category_2,
            "category_3": pr.category_3,
            "comment": pr.comment,
            "title_change": pr.title_change,
            "level_change": pr.level_change
        } for pr in prs ]
    )

    print("done!")