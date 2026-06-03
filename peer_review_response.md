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
- Rename title route handler to get_title
- Add explicit response models to remaining routes
- Move repeated existence checks and formatting into helpers
- Align Python version requirement with Render
- Remove API key debug print from auth.py
- Standardize create endpoints on 201 status codes
- Fix SQL injection vulnerability in comments.py by removing f-string formatting in SQL query
- Standardize SQL query return patterns to use .mappings() with dict() conversion consistently
- Rename employee list database result variable for readability
- Validate employee id and reviewer id before inserts/updates in performance_reviews.py
- Validate date ordering in performance reviews
- Add Company and PerformanceReview response models
- Remove default database credentials from db.py
- Return 204 with no response body for delete endpoints
- Make performance review delete return 404 if the review does not exist
- Make comment delete check that the comment exists before deleting
- Use database row id in get_employee instead of only using the path id

## Feedback kept as-is

- No shared data-access layer; duplicated patterns
  - We are not doing this because it is unnecessary for the current scope.

- Not using CORS
  - We do not need CORS because this API is not currently connected to a frontend. We used CORS in Potion Shop to connect to the Vercel frontend, but this project does not have that setup.

- No Idempotent, can INSERT same company multiple times
  - We know that repeated POST requests can create duplicate company rows. For this project, we are keeping company creation as a normal create operation because the API spec does not require company names to be unique or POST /companies to be idempotent.

- Early returns
  - We are not making this change because we want to keep the current validation pattern. The current code checks optional resources only when those query parameters are provided, which keeps the logic clear.

- Comment formatting helper is only used for comments
  - Shared formatting helpers are useful when database field names and API field names are different. Comments need a special formatter because fields like employee_id, commenter_id, and created_at are returned as employeeId, authorId, and createdAt. Most other resources already use the same field names in the database and response models.

- Single spec and inconsistent with itself / formatting inconsistency in APISpec.md
  - We will keep this in mind for future API specification updates. Cleaning the whole spec would be useful, but it is separate from the route fixes.

- Missing endpoints from v1 and v2 manual test results
  - The manual test result files do not fully cover the employee and title endpoints. We did not expand those files right now because the current focus was code review fixes.

- Conversions in performance_reviews.py
  - We chose to keep the explicit dict() conversion for consistency across the codebase. This ensures SQL mappings are uniformly converted to dictionaries before being used or returned.

- For loop inside database connection in both employees.py and titles.py
  - We are keeping this as-is because the query already calls .mappings().all(), which fetches the rows before the list conversion runs. The loop is only converting each row into a plain dictionary, not making more database calls. Keeping it near the query is easier to read and matches the simple style used in this project.

- We did not add automated tests.
    - We used manual curl testing instead to check auth, create, patch, invalid ratings, invalid dates, missing foreign keys, draft submit, and delete behavior.
