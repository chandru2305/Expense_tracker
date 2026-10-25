"""Main FastAPI Application Entry Point for Expense Tracker."""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.database import engine, Base
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables exist safely without deleting existing records
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Expense Tracker API & Dashboard",
    description="A robust, full-stack Expense Tracker application with SQLite, interactive dashboard, and automated tests.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include API routes
app.include_router(router, prefix="/api")
# Compatibility route aliases directly on root (e.g. /health, /expenses)
app.include_router(router)


# Custom Exception Handler to return clean JSON errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(x) for x in err.get("loc", [])])
        msg = err.get("msg")
        errors.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Mount static assets directory
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse, tags=["Frontend"])
def serve_dashboard():
    """Serve the primary responsive HTML dashboard."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_file):
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse(
        content="<h1>Expense Tracker</h1><p>Dashboard interface loading...</p>",
        status_code=200,
    )
