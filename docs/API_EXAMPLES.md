# API Examples

Open Swagger at `http://localhost:8000/docs` for the easiest interactive flow.

## Health

```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Create application

```bash
curl -X POST http://localhost:8000/applications \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "ABC Manufacturing Pvt Ltd",
    "business_type": "PRIVATE_LIMITED",
    "industry": "Manufacturing",
    "business_vintage_years": 7,
    "registration_number": "DEMO-REG-001",
    "tax_identifier": "DEMO-TAX-001",
    "declared_annual_revenue": 35000000,
    "declared_existing_obligations": 4000000,
    "loan_request": {
      "requested_amount": 5000000,
      "currency": "INR",
      "tenure_months": 60,
      "purpose": "Purchase of machinery",
      "proposed_interest_rate": 11.5,
      "collateral_offered": true
    },
    "consent_confirmed": true
  }'
```

Copy the returned `application_id`.

## Upload document

```bash
curl -X POST "http://localhost:8000/applications/APP_ID/documents" \
  -F "file=@data/synthetic/strong_case/bank_statement.txt"
```

Upload the other `.txt` files in the same sample case.

## Analyze

```bash
curl -X POST http://localhost:8000/applications/APP_ID/analyze
```

## Read results

```bash
curl http://localhost:8000/applications/APP_ID/analysis
curl http://localhost:8000/applications/APP_ID/profile
curl http://localhost:8000/applications/APP_ID/metrics
curl http://localhost:8000/applications/APP_ID/risk
curl http://localhost:8000/applications/APP_ID/policy
curl http://localhost:8000/applications/APP_ID/recommendation
curl http://localhost:8000/applications/APP_ID/audit
```

## What-if simulation

```bash
curl -X POST http://localhost:8000/applications/APP_ID/simulate \
  -H "Content-Type: application/json" \
  -d '{"amount":4000000,"currency":"INR","interest_rate":11.5,"tenure_months":60}'
```

## Human decision

```bash
curl -X POST http://localhost:8000/applications/APP_ID/decision \
  -H "Content-Type: application/json" \
  -H "X-User-ID: demo-underwriter" \
  -d '{"action":"APPROVE","comments":"Reviewed synthetic evidence","conditions":[],"override_reason":null}'
```
