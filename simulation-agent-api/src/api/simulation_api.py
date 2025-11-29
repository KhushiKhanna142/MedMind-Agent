"""
Simulation Agent FastAPI Application
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
from datetime import datetime

from src.api.routes.simulation_routes import router as simulation_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Simulation Agent API",
    description="""
    REST API for the Medical Simulation Agent
    
    This API provides endpoints for:
    - Generating clinical simulation questions
    - Loading benchmark answers
    - Comparing model answers with benchmarks
    - Running complete simulation workflows
    - Analyzing errors and generating improvement suggestions
    
    Perfect for testing and evaluating medical AI models!
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Simulation Agent Team",
    },
    license_info={
        "name": "MIT",
    }
)

# Configure CORS - Allow all origins for easy sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development/sharing
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(simulation_router)


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint - API information
    """
    return {
        "message": "Welcome to the Simulation Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/simulation/health",
        "timestamp": datetime.now().isoformat()
    }


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors with detailed messages
    """
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "body": exc.body
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle general exceptions
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "detail": str(exc)
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup
    """
    logger.info("=" * 60)
    logger.info("Simulation Agent API Starting...")
    logger.info("=" * 60)
    logger.info("Version: 1.0.0")
    logger.info("Docs available at: /docs")
    logger.info("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown
    """
    logger.info("Simulation Agent API Shutting Down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
