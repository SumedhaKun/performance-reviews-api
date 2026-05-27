employees

1. GET /employees
Response:
[{
	“id”: id,
	“firstName”: string,
	“lastName”: string,
	“level”: int,
	“reportsTo”: id,
	“createdAt”: Date
}]

2. GET /employees/{employee_id}
Response:
{
	“id”: id,
	“firstName”: string,
	“lastName”: string,
	“level”: int,
	“reportsTo”: id,
	“createdAt”: Date
}

3. POST /employees
Request:
{
	“firstName”: string,
	“lastName”: string,
	“level”: int,
	“reportsTo”: id
}
Response:
{
	“id”: id,
	“firstName”: string,
	“lastName”: string,
	“level”: int,
	“reportsTo”: id,
	“createdAt”: Date
}

4. DELETE /employees/{employee_id}
	<No Response>


performance_reviews

5. GET /performance_reviews/
Parameters (at least 1 is required):
authorId: id
employeeId: id 
Response:
[{
  "id": id,
  "employeeId": id,
  "level": int,
  "overall": int,
  "categories": {
    "teamWork": int,
    "timeManagement": int,
    "innovation": int
  },
  "meetingDate": Date,
  "meetingSupervisorId": id,
  "result": string,
  "comments": string,
  "author": id,
  "createdAt": Date
}]

6. GET /performance_reviews/{review_id}
Response:
{	
  “id”: id
	“employeeId”: id,
  “level”: int,
	“overall”: int,
	“categories”: {
    “teamWork”: int,
	  “timeManagement”: int,
	  “innovation”: int,
  },
	“meetingDate”: Date,
	“meetingSupervisorId”: id,
	“result”: string,
	“comments”: string
	“authorId”: id
	“createdAt”: Date
}

7. POST /performance_reviews
Request:
{
  “employeeId”: int,
  “level”: int,
	“overall”: int,
	“categories”: {
    “teamWork”: int,
	  “timeManagement”: int,
	  “innovation”: int
  },
	“meetingDate”: Date,
	“meetingSupervisorId”: id,
	“result”: string,
	“comments”: string,
	“author”: id
}
Response:
{
	“id”: id
	“employeeId”: int,
  “level”: int,
	“overall”: int,
	“categories”: {
    “teamWork”: int,
	  “timeManagement”: int,
	  “innovation”: int,
  },
	“meetingDate”: Date,
	“meetingSupervisorId”: id,
	“result”: string,
	“comments”: string,
	“author”: id,
	“createdAt”: Date
}
	
8. DELETE /performance_reviews/{review_id}
  <No response>

comments

9. POST /comments/
	Request:
	{
		“employeeId”: id,
		“subject”: string,
		“comment”: string,
		“authorId”: id
	}
	Response:
	{
	“id”: int,
		“employeeId”: id,
		“subject”: string,
		“comment”: string,
		“authorId”: id,
		“createdAt”: Date
}

10. GET /comment/
Parameters (at least 1 is required):
authorId: id
employeeId: id 
Response:
[{
	“id”: int,
		“employeeId”: id,
		“subject”: string,
		“comment”: string,
		“authorId”: id,
		“createdAt”: Date
}]

11. GET /comment/{comment_id}
Response Body:
{
	“id”: int,
	“employeeId”: id,
	“subject”: string,
	“comment”: string,
	“authorId”: id,
	“createdAt”: Date
}
DELETE /comments/{comment_id}

	<No Response>


###complex endpoints

12. GET /employees/{employee_id}/stats
optional query parameters:
start_date: Date
end_date: Date

If start_date is not provided, it defaults to the employee's hire_date.
If end_date is not provided, it defaults to today's date.

Response:
{
  "employee_id": id,
  "company_id": id,
  "first_name": string,
  "last_name": string,
  "department": string,
  "start_date": Date,
  "end_date": Date,
  "total_reviews": int,
  "average_category_1": float,
  "average_category_2": float,
  "average_category_3": float,
  "title_change_count": int,
  "title_change_rate": float,
  "level_change_count": int,
  "level_change_rate": float
}

13. GET /companies/{company_id}/departments/{department}/stats
Optional query parameters:
start_date: Date
end_date: Date

If start_date is not provided, it defaults to the company's founded_date. If
the company has no founded_date, it defaults to the earliest hire_date in that
department. If end_date is not provided, it defaults to today's date.

Response:
{
  "company_id": id,
  "department": string,
  "start_date": Date,
  "end_date": Date,
  "employee_count": int,
  "total_reviews": int,
  "average_category_1": float,
  "average_category_2": float,
  "average_category_3": float,
  "title_change_count": int,
  "title_change_rate": float,
  "level_change_count": int,
  "level_change_rate": float
}
