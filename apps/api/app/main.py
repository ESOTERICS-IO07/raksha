"""RAKSHA FastAPI application entry point.

Registers all v1 routers and global exception handlers.
"""

from __future__ import annotations

import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1 import transactions, users, recipients, scenarios, dashboard
from app.schemas.errors import ErrorDetail, ErrorResponse

app = FastAPI(
    title="RAKSHA API",
    description="Fraud intelligence and adaptive friction platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── v1 routers ────────────────────────────────────────────────────────────────
_v1_prefix = "/api/v1"

app.include_router(transactions.router, prefix=_v1_prefix)
app.include_router(users.router, prefix=_v1_prefix)
app.include_router(recipients.router, prefix=_v1_prefix)
app.include_router(scenarios.router, prefix=_v1_prefix)
app.include_router(dashboard.router, prefix=_v1_prefix)


# ── Global exception handlers ─────────────────────────────────────────────────

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Unwrap our structured ErrorResponse from HTTPException.detail."""
    detail = exc.detail
    # If we raised with a structured ErrorResponse dict, return it directly
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    # Fallback for plain string details
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                code="HTTP_ERROR",
                message=str(detail),
                request_id=str(uuid.uuid4()),
            )
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return contract-compliant error responses for Pydantic validation failures."""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error=ErrorDetail(
                code="VALIDATION_ERROR",
                message=str(exc.errors()[0].get("msg", "Validation error")),
                request_id=str(uuid.uuid4()),
            )
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Catch-all handler — never leak stack traces or DB credentials."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error=ErrorDetail(
                code="INTERNAL_ERROR",
                message="An unexpected error occurred.",
                request_id=str(uuid.uuid4()),
            )
        ).model_dump(),
    )


# ── Health / root ─────────────────────────────────────────────────────────────

@app.get("/")
def root() -> dict:
    return {"service": "raksha-api", "status": "ok"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "raksha-api"}