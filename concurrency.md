## Case 1: PATCH /performance-review/{review-id}

Two processes try and update the same performance review at the same time, while seperating the reads from the updates.

Code Example:

```
# read performance review
select_query = connection.execute(sqlalchemy.text("""
    SELECT id, employee_id, review_period_start, review_period_end,
           review_date, reviewer_id, overall_rating, category_1,
           category_2, category_3, comment, title_change, level_change
    FROM performance_reviews
    WHERE id = :review_id
    """)).fetchone()

# update performance review
review = dict(result) # assume score was 3
review["overall_rating"] = 4
review["comment"] = "Improved performance this cycle"

# Another process makes an update here, updates score to 2

update_query = sqlalchemy.text(f"""
    UPDATE performance_reviews
    SET {set_clause}
    WHERE id = :review_id
""")
# overwrites other process's score -> lost update
```

### Protection:

Read and modify in the same locked step.

Code Example:

```
query = sqlalchemy.text(f"""
        UPDATE performance_reviews
        SET {set_clause}
        WHERE id = :review_id
        RETURNING id, employee_id, review_period_start, review_period_end,
            review_date, reviewer_id, overall_rating, category_1, category_2,
            category_3, comment, title_change, level_change
    """)
```

Read and modify are all in the same step so it's locked and no other process is going to modify the data in the middle of reading and updating.

## Case 2: GET /employee/stats

Could get average rating for employees, and then in another transaction, get total employees. In between these, there could have been an update to employees, and now there are inconsistent results.

Code Example:

```
with db.engine.begin() as connection:
        averages = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    AVG(category_1) AS average_category_1,
                    AVG(category_2) AS average_category_2,
                    AVG(category_3) AS average_category_3,
                FROM performance_reviews
                WHERE employee_id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        ).one_or_none()

# Another transaction adds an employee

with db.engine.begin() as connection:
        perf_revs = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    COUNT(*) AS total
                FROM performance_reviews
                WHERE employee_id = :employee_id
                """
            ),
            {"employee_id": employee_id},
        ).one_or_none()

```

This is a repeatable read issue.

### Protection:

```
with db.engine.begin() as connection:
    stats = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    COUNT(id) AS total_reviews,
                    AVG(category_1) AS average_category_1,
                    AVG(category_2) AS average_category_2,
                    AVG(category_3) AS average_category_3,
                    COUNT(*) FILTER (
                        WHERE title_change = 1
                    ) AS title_change_count,
                    COUNT(*) FILTER (
                        WHERE level_change = 1
                    ) AS level_change_count
                FROM performance_reviews
                WHERE employee_id = :employee_id
                    AND (:start_date IS NULL OR review_date >= :start_date)
                    AND (:end_date IS NULL OR review_date <= :end_date)
                """
            ),
            {
                "employee_id": employee_id,
                "start_date": effective_start_date,
                "end_date": effective_end_date,
            },
        ).mappings().one()
```

Keep it all in one transaction and have the isolation level be 'Repeatable Read' (PostgreSQL already does this) so that everything in that transaction sees/uses the same rows.

## Case 3:
