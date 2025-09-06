# Excel API UANL

This FastAPI application reads data from an Excel file and exposes it as a JSON API.

## Endpoint

- `GET /llamadas`: Returns all call records from the Excel file.

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
