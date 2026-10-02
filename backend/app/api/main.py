from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from sqlalchemy import text

from app.api.errors import general_exception_handler
from app.api.limiter import limiter
from app.api.routes import router
from app.database.database import SessionLocal

# for admin dashboard
from app.api.admin.routes import router as admin_router


app = FastAPI(
    title="BrightSmile Dental AI API",
    description="Backend API for the BrightSmile Dental AI Receptionist.",
    version="1.0.0",
)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# Rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(
    request: Request,
    exc: RateLimitExceeded,
):
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
        },
    )


# General error handling
app.add_exception_handler(
    Exception,
    general_exception_handler,
)


# API routes
app.include_router(router, prefix="/api")
app.include_router(admin_router, prefix="/api")


# Health check
@app.get("/health")
def health_check():

    db_status = "ok"

    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()

    except Exception:
        db_status = "error"

    return {
        "status": "ok",
        "service": "BrightSmile Dental AI API",
        "database": db_status,
    }


"""
API architecture:
        app/
        │
        ├── agent/
        │   └── agent.py
        │
        ├── api/
        │   ├── __init__.py
        │   ├── main.py       ← FastAPI application
        │   ├── routes.py     ← API endpoints
        │   └── schemas.py    ← Request/response models
        │
        ├── database/
        │   ├── database.py
        │   ├── models.py
        │   └── seed.py
        │
        ├── knowledge/
        │
        ├── memory/
        │
        ├── services/
        │
        └── tools/
            ├── appointments.py
            ├── basic.py
            └── search.py

        
                    FastAPI
                       │
              ┌────────┴────────┐
              │                 │
           /health            /api/chat
              │                 │
              ▼                 ▼
           MySQL            LangGraph
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
                 RAG/Search   Doctors   Appointments
                                            │
                                            ▼
                                          MySQL
"""