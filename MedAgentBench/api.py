"""
MedAgentBench API - FastAPI wrapper for MedAgentBench evaluation agent

This API provides REST endpoints to:
- Run model evaluations
- Check evaluation status
- Retrieve evaluation results
- Upload test data
"""

import logging
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel, Field

from agent import MedAgentBench, create_agent
from config import MedAgentBenchConfig
from thresholds import EvaluationThresholds

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MedAgentBench API",
    description="REST API for medical AI model evaluation using MedAgentBench",
    version="1.0.0"
)

# Global agent instance
agent: Optional[MedAgentBench] = None

# Store evaluation results in memory (in production, use a database)
evaluation_results: Dict[str, Dict[str, Any]] = {}
evaluation_status: Dict[str, str] = {}


# Request/Response Models
class EvaluationRequest(BaseModel):
    """Request model for evaluation"""
    test_data_path: str = Field(..., description="Path to test JSONL file")
    model_endpoint_url: str = Field(..., description="Model endpoint URL")
    model_endpoint_type: str = Field(default="fastapi", description="Type of endpoint (fastapi, vertex_ai, custom)")
    model_name: Optional[str] = Field(None, description="Name of the model being evaluated")
    evaluation_id: Optional[str] = Field(None, description="Optional custom evaluation ID")
    max_test_cases: Optional[int] = Field(None, description="Maximum number of test cases to evaluate")


class EvaluationResponse(BaseModel):
    """Response model for evaluation submission"""
    evaluation_id: str
    status: str
    message: str
    started_at: str


class EvaluationStatusResponse(BaseModel):
    """Response model for evaluation status"""
    evaluation_id: str
    status: str
    progress: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class EvaluationResultResponse(BaseModel):
    """Response model for evaluation results"""
    evaluation_id: str
    model_name: Optional[str]
    evaluation_status: str
    metrics: Dict[str, float]
    safety_score: float
    total_test_cases: int
    successful_predictions: int
    failed_predictions: int
    certificate_path: Optional[str]
    report_path: Optional[str]
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    agent_initialized: bool
    timestamp: str


class ConfigUpdateRequest(BaseModel):
    """Request to update agent configuration"""
    model_endpoint_url: Optional[str] = None
    certificate_output_path: Optional[str] = None
    report_output_path: Optional[str] = None
    max_test_cases: Optional[int] = None


# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize the agent on startup"""
    global agent
    try:
        logger.info("Initializing MedAgentBench agent...")
        config = MedAgentBenchConfig()
        agent = create_agent(config)
        logger.info("✅ MedAgentBench agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "MedAgentBench API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if agent is not None else "not_initialized",
        agent_initialized=agent is not None,
        timestamp=datetime.now().isoformat()
    )


@app.post("/evaluate", response_model=EvaluationResponse)
async def start_evaluation(
    request: EvaluationRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a new evaluation asynchronously
    
    The evaluation runs in the background and you can check its status
    using the /status/{evaluation_id} endpoint.
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Generate evaluation ID if not provided
    eval_id = request.evaluation_id or f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Check if evaluation ID already exists
    if eval_id in evaluation_status:
        raise HTTPException(
            status_code=400,
            detail=f"Evaluation ID {eval_id} already exists. Use a different ID."
        )
    
    # Mark as running
    started_at = datetime.now().isoformat()
    evaluation_status[eval_id] = "running"
    
    # Add background task
    background_tasks.add_task(
        run_evaluation,
        eval_id=eval_id,
        request=request,
        started_at=started_at
    )
    
    return EvaluationResponse(
        evaluation_id=eval_id,
        status="running",
        message="Evaluation started successfully",
        started_at=started_at
    )


@app.get("/status/{evaluation_id}", response_model=EvaluationStatusResponse)
async def get_evaluation_status(evaluation_id: str):
    """Get the status of an evaluation"""
    if evaluation_id not in evaluation_status:
        raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found")
    
    status = evaluation_status[evaluation_id]
    result = evaluation_results.get(evaluation_id, {})
    
    return EvaluationStatusResponse(
        evaluation_id=evaluation_id,
        status=status,
        progress=result.get("progress"),
        started_at=result.get("started_at"),
        completed_at=result.get("completed_at")
    )


@app.get("/results/{evaluation_id}", response_model=EvaluationResultResponse)
async def get_evaluation_results(evaluation_id: str):
    """Get the results of a completed evaluation"""
    if evaluation_id not in evaluation_status:
        raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found")
    
    if evaluation_status[evaluation_id] == "running":
        raise HTTPException(
            status_code=400,
            detail=f"Evaluation {evaluation_id} is still running. Check /status/{evaluation_id}"
        )
    
    if evaluation_id not in evaluation_results:
        raise HTTPException(status_code=404, detail=f"Results for {evaluation_id} not found")
    
    result = evaluation_results[evaluation_id]
    
    return EvaluationResultResponse(
        evaluation_id=result.get("evaluation_id", evaluation_id),
        model_name=result.get("model_name"),
        evaluation_status=result.get("evaluation_status", "UNKNOWN"),
        metrics=result.get("metrics", {}),
        safety_score=result.get("safety_score", 0.0),
        total_test_cases=result.get("total_test_cases", 0),
        successful_predictions=result.get("successful_predictions", 0),
        failed_predictions=result.get("failed_predictions", 0),
        certificate_path=result.get("certificate_path"),
        report_path=result.get("report_path"),
        timestamp=result.get("timestamp", "")
    )


@app.get("/certificate/{evaluation_id}")
async def download_certificate(evaluation_id: str):
    """Download the PDF certificate for an evaluation"""
    if evaluation_id not in evaluation_results:
        raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found")
    
    result = evaluation_results[evaluation_id]
    cert_path = result.get("certificate_path")
    
    if not cert_path or not os.path.exists(cert_path):
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    return FileResponse(
        cert_path,
        media_type="application/pdf",
        filename=f"certificate_{evaluation_id}.pdf"
    )


@app.get("/report/{evaluation_id}")
async def download_report(evaluation_id: str):
    """Download the JSON report for an evaluation"""
    if evaluation_id not in evaluation_results:
        raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found")
    
    result = evaluation_results[evaluation_id]
    report_path = result.get("report_path")
    
    if not report_path or not os.path.exists(report_path):
        raise HTTPException(status_code=404, detail="Report not found")
    
    return FileResponse(
        report_path,
        media_type="application/json",
        filename=f"report_{evaluation_id}.json"
    )


@app.get("/evaluations")
async def list_evaluations():
    """List all evaluations"""
    evaluations = []
    for eval_id, status in evaluation_status.items():
        result = evaluation_results.get(eval_id, {})
        evaluations.append({
            "evaluation_id": eval_id,
            "status": status,
            "model_name": result.get("model_name"),
            "started_at": result.get("started_at"),
            "completed_at": result.get("completed_at")
        })
    
    return {"evaluations": evaluations, "total": len(evaluations)}


@app.delete("/evaluations/{evaluation_id}")
async def delete_evaluation(evaluation_id: str):
    """Delete an evaluation and its results"""
    if evaluation_id not in evaluation_status:
        raise HTTPException(status_code=404, detail=f"Evaluation {evaluation_id} not found")
    
    # Remove from storage
    evaluation_status.pop(evaluation_id, None)
    evaluation_results.pop(evaluation_id, None)
    
    return {"message": f"Evaluation {evaluation_id} deleted successfully"}


@app.post("/config")
async def update_config(config_update: ConfigUpdateRequest):
    """Update agent configuration"""
    global agent
    
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")
    
    # Get current config
    current_config = agent.get_config()
    
    # Update with new values
    if config_update.model_endpoint_url:
        current_config["model_endpoint_url"] = config_update.model_endpoint_url
    if config_update.certificate_output_path:
        current_config["certificate_output_path"] = config_update.certificate_output_path
    if config_update.report_output_path:
        current_config["report_output_path"] = config_update.report_output_path
    if config_update.max_test_cases:
        current_config["max_test_cases"] = config_update.max_test_cases
    
    # Recreate agent with new config
    new_config = MedAgentBenchConfig(**current_config)
    agent = create_agent(new_config)
    
    return {"message": "Configuration updated successfully", "config": current_config}


# Background Task Functions

async def run_evaluation(eval_id: str, request: EvaluationRequest, started_at: str):
    """
    Background task to run evaluation
    """
    try:
        logger.info(f"Starting evaluation {eval_id}")
        
        # Store start time
        evaluation_results[eval_id] = {
            "started_at": started_at,
            "progress": "Running evaluation..."
        }
        
        # Run evaluation
        result = agent.evaluate(
            test_data_path=request.test_data_path,
            model_endpoint_url=request.model_endpoint_url,
            model_endpoint_type=request.model_endpoint_type,
            model_name=request.model_name,
            evaluation_id=eval_id,
            max_test_cases=request.max_test_cases
        )
        
        # Store results
        result["started_at"] = started_at
        result["completed_at"] = datetime.now().isoformat()
        evaluation_results[eval_id] = result
        
        # Update status
        evaluation_status[eval_id] = "completed"
        
        logger.info(f"✅ Evaluation {eval_id} completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Evaluation {eval_id} failed: {e}")
        
        # Store error
        evaluation_results[eval_id] = {
            "started_at": started_at,
            "completed_at": datetime.now().isoformat(),
            "error": str(e),
            "evaluation_status": "FAILED"
        }
        evaluation_status[eval_id] = "failed"


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
