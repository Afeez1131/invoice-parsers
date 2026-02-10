import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from middleware import RequestSizeLimitMiddleware
from router import router as parser_router
from schemas import ErrorResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_PAYLOAD_SIZE = 5  # IN MB
# Initialize FastAPI app
app = FastAPI(
    title="Invoice Parser API",
    description="API for parsing unstructured invoice text",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include
app.include_router(parser_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "invoice-parser",
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Invoice Parser API",
        "version": "1.0.0",
        "endpoints": {
            "/parse": "POST - Parse invoice text",
            "/parse/raw": "POST - Parse with raw JSON input",
            "/health": "GET - Health check",
            "/docs": "API documentation",
        },
    }


app.add_middleware(RequestSizeLimitMiddleware, max_body_size_mb=MAX_PAYLOAD_SIZE)


# Custom rate limit exceeded handler
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please wait for few minutes then try again.",
        },
    )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            ErrorResponse(error=exc.detail, timestamp=datetime.now().isoformat())
        ),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(
            ErrorResponse(
                error="Internal server error",
                detail=str(exc),
                timestamp=datetime.now().isoformat(),
            )
        ),
    )
