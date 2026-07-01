"""
Application Entry Point

Author: Aman Maurya
Project: 3R Analyzer Intelligence
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.jobs import router as jobs_router
from app.api.process import router as process_router

from app.core.dependencies import (
    get_scheduler_service,
)

from app.database.init_db import initialize_database

from app.utils.logger import logger


# ==========================================================
# Application Lifecycle
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.
    """

    logger.info("=" * 80)
    logger.info("Starting 3R Analyzer Intelligence...")

    # -----------------------------------------------------------------
    # NOTE:
    # initialize_database() is kept only for local development.
    # Replace this with Alembic migrations before production deployment.
    # -----------------------------------------------------------------
    initialize_database()

    scheduler = get_scheduler_service()

    scheduler.start()

    logger.info("Application startup completed successfully.")

    yield

    logger.info("Stopping application...")

    scheduler.shutdown()

    logger.info("Application shutdown completed.")


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title="3R Analyzer Intelligence",
    version="0.3.0",
    description="Recurring Incident Intelligence Platform",
    lifespan=lifespan
)


# ==========================================================
# API Routers
# ==========================================================

app.include_router(process_router)

app.include_router(jobs_router)


# ==========================================================
# Root Endpoint
# ==========================================================

@app.get("/", tags=["Application"])
def root() -> dict:
    """
    Health check endpoint.
    """

    return {
        "status": "Running",
        "application": "3R Analyzer Intelligence",
        "version": "0.3.0"
    }