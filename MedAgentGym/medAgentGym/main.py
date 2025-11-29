from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
from dotenv import load_dotenv
from vertex_setup import init_vertex_ai, train_sft_job

# Load env vars and setup Vertex AI
try:
    init_vertex_ai()
except Exception as e:
    print(f"Error setting up Vertex AI: {e}")


app = FastAPI()

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None

class SFTRequest(BaseModel):
    model_id: str
    dataset_path: str
    epochs: Optional[int] = 3
    tuned_model_display_name: Optional[str] = None

@app.post("/run/sft")
async def run_sft(request: SFTRequest):
    try:
        result = train_sft_job(
            request.model_id, 
            request.dataset_path, 
            request.epochs,
            request.tuned_model_display_name
        )

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

class DeployRequest(BaseModel):
    model_name: str
    machine_type: Optional[str] = "g2-standard-12"

@app.post("/deploy")
async def deploy_model(request: DeployRequest):
    try:
        from vertex_setup import deploy_tuned_model
        endpoint_name = deploy_tuned_model(request.model_name, request.machine_type)
        return {"status": "deploying", "endpoint_name": endpoint_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
