# Ignite Knowledge - Backend

## Setup

```
cd backend
poetry install
poetry run uvicorn app.main:app --reload --port 8080
```

## Endpoints
- `GET /health`
- `POST /export` → { filename, format: 'csv'|'pdf', items: [] }

## Notes
- PDF generation via WeasyPrint, CSV built-in.

