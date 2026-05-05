# Example workflow
Example workflow: Add a new company

I am setting up the performance review system for a company. I want to add the company to the database and then verify that it was added correctly.

POST /companies

I pass in the following information and get the new company object back:

{
    "name": "HELLO",
    "industry": "Software",
    "headquarters_location": "San Luis Obispo, CA",
    "founded_date": "2026-05-04",
    "active": true
}

I can also now get the company by its id.

GET /companies/{company_id}

# Testing results

1. The curl statement called:

```bash
curl -X 'POST' \
  'https://performance-reviews-api.onrender.com/companies' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "name": "HELLO",
  "industry": "Software",
  "headquarters_location": "San Luis Obispo, CA",
  "founded_date": "2026-05-04",
  "active": true
}'
```

2. The response received:

```json
{
  "id": 2,
  "name": "HELLO",
  "industry": "Software",
  "headquarters_location": "San Luis Obispo, CA",
  "founded_date": "2026-05-04",
  "active": true
}
```

3. The curl statement called:

```bash
curl -X 'GET' \
  'https://performance-reviews-api.onrender.com/companies/2' \
  -H 'accept: application/json'
```

4. The response received:

```json
{
  "id": 2,
  "name": "HELLO",
  "industry": "Software",
  "headquarters_location": "San Luis Obispo, CA",
  "founded_date": "2026-05-04",
  "active": true
}
```
