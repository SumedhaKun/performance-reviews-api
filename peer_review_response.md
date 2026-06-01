## Feedback addressed: Code Reviews

- Remove unused Imports in performace_reviews.py
- Stop use of list-style parameter passing for single inserts/deletes in some places.
- Remove debug logging from production code
- The employee insert query uses shortened parameter names like cid, fn, ln, tid, and dep. More descriptive names like company_id, first_name, and department would help improve readability.
- Use FastApi Prefix router
- Implement authentication middleware
- Validate foreign keys (company id and title id) before inserts in employees.py
- Standardize delete behavior across routes
- Delete PRs and comments associated to an employee when the employee is deleted
- Route prefixes to plural names
- Standardize direct row returns to mappings
- Validate overall rating range in performance reviews
- Change employee phone numbers to validated strings
- Use date consistently across employee, company, and review date fields
- Fix misleading docstrings and add missing route docstrings
- Standardize route trailing slash style to /smth/
