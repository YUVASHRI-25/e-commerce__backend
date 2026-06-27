# E-Commerce Backend

A FastAPI backend for an e-commerce application. The API is organized into routers for authentication, addresses, categories, products, cart, orders, and payments.

## Features

- FastAPI application with automatic interactive docs
- SQLAlchemy models and database initialization
- Routers for core commerce workflows
- PostgreSQL-backed persistence

## Tech Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Uvicorn

## Project Structure

```text
app/
  main.py          # FastAPI app entrypoint
  database.py      # SQLAlchemy engine, session, and base
  models/          # Database models
  routers/         # API route modules
  schemas/         # Pydantic schemas
  utils/           # Hashing and token helpers
```

## Prerequisites

- Python 3.10+ recommended
- PostgreSQL installed and running
- A database named `ecommerce_db`

## Setup

1. Create and activate a virtual environment.

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure PostgreSQL is available at the connection string in `app/database.py`.

   The current default is:

   ```text
   postgresql://postgres:yuva@localhost:5432/ecommerce_db
   ```

4. Start the API:

   ```bash
   uvicorn app.main:app --reload
   ```

## API Docs

Once the server is running, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Notes

- Database tables are created on startup via `Base.metadata.create_all(bind=engine)` in `app/main.py`.
- If you want to use different database credentials or host settings, update `app/database.py`.