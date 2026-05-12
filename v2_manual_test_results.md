# Example workflow 2: Add a comment

My employee has spent 2 weeks at work, so it is time for their second comment. First, I will create an employee and verify that I got the right employee ID.

POST /employees/

```bash
curl -X 'POST' \
  'https://performance-reviews-api.onrender.com/employees/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "company_id": 1,
  "first_name": "pihu",
  "last_name": "jha",
  "email": "pihu@gmail.com",
  "phone": 1,
  "title_id": 1,
  "level": 32,
  "department": "cs",
  "hire_date": "2055-05-05",
  "current_employee": true
}'
```

Returns

```json
{"id":6,"company_id":1,"first_name":"pihu","last_name":"jha","email":"pihu@gmail.com","phone":1,"title_id":1,"level":32,"department":"cs","hire_date":"2055-05-05","current_employee":true}
```

That is the right employee, so I will add their comment.

POST /comment/

```bash
curl -X 'POST' \
  'https://performance-reviews-api.onrender.com/comment/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "employeeId": 5,
  "subject": "testing comment",
  "comment": "this is the comment",
  "authorId": 5
}'
```

Response:

```json
{"id":2,"employeeId":5,"subject":"testing comment","comment":"this is the comment","authorId":5,"createdAt":"2026-05-12T04:54:21.106835"}
```

Now, I want to see all the comments for this employee.

GET /comment/

Parameters:

```text
employeeId: 5
```

```bash
curl -X 'GET' \
  'https://performance-reviews-api.onrender.com/comment/?employeeId=5' \
  -H 'accept: application/json'
```

Result:

```json
[
  {"id":2,"employeeId":5,"subject":"testing comment","comment":"this is the comment","authorId":5,"createdAt":"2026-05-12T04:54:21.106835"},{"id":1,"employeeId":5,"subject":"testing comment","comment":"this is the comment","authorId":5,"createdAt":"2026-05-12T04:40:40.516497"}
]
```

I can also get this specific comment by its comment ID.

GET /comment/1

```bash
curl -X 'GET' \
  'https://performance-reviews-api.onrender.com/comment/1' \
  -H 'accept: application/json'
```

Result:

```json
{"id":1,"employeeId":5,"subject":"testing comment","comment":"this is the comment","authorId":5,"createdAt":"2026-05-12T04:40:40.516497"}
```

I can see that my comment got added correctly.
