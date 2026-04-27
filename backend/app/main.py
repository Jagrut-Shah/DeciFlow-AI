import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import CustomException, custom_exception_handler, generic_exception_handler
from app.core.middleware import RequestLoggingMiddleware, SecurityHeadersMiddleware
from app.schemas.response import success_response, APIResponse
from app.core.dependencies import require_role

# --- Uptime tracking ---
from datetime import datetime, timezone
BOOT_TIME = datetime.now(timezone.utc)

def get_uptime_string() -> str:
    """Returns a formatted duration since BOOT_TIME."""
    delta = datetime.now(timezone.utc) - BOOT_TIME
    days, remainder = divmod(int(delta.total_seconds()), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    
    return " ".join(parts)

# 1. Setup logging first — before any other imports that might log
setup_logging()
logger = logging.getLogger(__name__)
logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]")

# --------------------------------------------------------------------------- #
# Rate Limiter — shared limiter instance, 60 req/min by default               #
# --------------------------------------------------------------------------- #
limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])


# 2. Application Lifespan — startup + graceful shutdown
from app.core.dependencies import get_task_queue, get_task_registry, get_pipeline_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("Starting background queue consumers...")
    queue = get_task_queue()
    registry = get_task_registry()
    registry.register("workflow_pipeline", get_pipeline_worker())
    await queue.start_consuming(concurrency=3)
    logger.info("Queue consumers started.")

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("Shutting down queue consumers...")
    await queue.stop_consuming()
    logger.info("Queue consumers stopped. Goodbye.")


# 3. Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
    # Hide default server error details in production
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
)

# Attach rate limiter state + 429 handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# 4. Middleware (order matters — outermost runs first on request, last on response)
app.add_middleware(SecurityHeadersMiddleware)    # Step 2: add security headers
app.add_middleware(RequestLoggingMiddleware)     # Step 1: trace ID + logging

# Trusted host protection — prevents Host-header injection attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,   # 👈 MUST be False with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)



# 5. Exception Handlers
app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)         # Catch-all — no stack trace leaks


# 6. Core Routes
@app.get("/health", tags=["System"], response_model=APIResponse)
@limiter.exempt
async def health_check():
    """Health check endpoint. No rate limit applied."""
    return success_response(
        data={"service": settings.PROJECT_NAME, "status": "operational",
              "version": settings.VERSION, "env": settings.ENVIRONMENT},
        message="Backend is healthy and operational.",
    )


@app.get("/metrics", tags=["System"], response_model=APIResponse)
async def get_metrics(
    request: Request,
    _admin: dict = Depends(require_role("admin")),
):
    """
    Returns an in-memory snapshot of application metrics.
    Requires a valid Bearer JWT with role='admin'.
    """
    from app.observability.metrics import metrics
    return success_response(
        data=metrics.get_snapshot(),
        message="Application metrics retrieved successfully."
    )


# 7. Include API Routers
from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.API_V1_STR)
