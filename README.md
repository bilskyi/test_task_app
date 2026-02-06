# Contributing to Travel Planner

Thank you for your interest in contributing to the Travel Planner API! This document provides guidelines for development and contributions.

## Development Setup

### Prerequisites
- Python 3.11 or higher
- Git

### Local Development

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/bilskyi/test_task_app.git
   cd test_task_app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
4. **Setup Environment**
   ```bash
   touch .env
   # paste this DATABASE_URL=sqlite:///db.sqlite3
   ```
   
5. **Run the application**
   ```bash
   fastapi dev
   ```
   or
   ```
   uvicorn app.main:app --reload
   ```
## Project Structure

```
test_task_app/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── db.py                # Database configuration
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routes/              # API route handlers
│   └── services/            # External service integrations
├── postman_collection.json  # Postman collection
├── requirements.txt         # Python dependencies
├── .gitignore               # gitignore file
└── README.md                # Project documentation
```

## Testing

### Manual Testing

Test with Postman:
1. Import `postman_collection.json`
2. Run the collection

## API Documentation

The API documentation is auto-generated from code:
- FastAPI automatically generates OpenAPI schema
- Access at `/docs` (Swagger UI) or `/redoc`
