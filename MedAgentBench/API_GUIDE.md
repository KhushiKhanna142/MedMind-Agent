# MedAgentBench API Documentation

## Overview

FastAPI-based REST API for MedAgentBench evaluation agent.

**Base URL**: `http://localhost:8001`  
**API Docs**: `http://localhost:8001/docs`

---

## Quick Start

### 1. Install Dependencies

```bash
cd agents/agent_3_benchmark
pip3 install -r api_requirements.txt
```

### 2. Start the API Server

```bash
python3 -m agents.agent_3_benchmark.api
# OR
uvicorn agents.agent_3_benchmark.api:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Test the API

```bash
curl http://localhost:8001/health
```

---

## API Endpoints

### Health & Info

#### `GET /`
Root endpoint with API information.

**Response**:
```json
{
  "message": "MedAgentBench API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

#### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "timestamp": "2025-11-27T17:40:00"
}
```

---

### Evaluation Workflow

#### `POST /evaluate`
Start a new evaluation (async).

**Request**:
```json
{
  "test_data_path": "data/test/sample_benchmark.jsonl",
  "model_endpoint_url": "http://localhost:8000/predict",
  "model_endpoint_type": "fastapi",
  "model_name": "MyMedicalModel_v1",
  "max_test_cases": 50
}
```

**Response**:
```json
{
  "evaluation_id": "eval_20251127_174000",
  "status": "running",
  "message": "Evaluation started successfully",
  "started_at": "2025-11-27T17:40:00"
}
```

#### `GET /status/{evaluation_id}`
Check evaluation status.

**Response**:
```json
{
  "evaluation_id": "eval_20251127_174000",
  "status": "running",
  "progress": "Running evaluation...",
  "started_at": "2025-11-27T17:40:00",
  "completed_at": null
}
```

**Status values**: `running`, `completed`, `failed`

#### `GET /results/{evaluation_id}`
Get evaluation results (only when completed).

**Response**:
```json
{
  "evaluation_id": "eval_20251127_174000",
  "model_name": "MyMedicalModel_v1",
  "evaluation_status": "PASS",
  "metrics": {
    "accuracy": 0.92,
    "precision": 0.89,
    "recall": 0.91,
    "f1_score": 0.90
  },
  "safety_score": 0.95,
  "total_test_cases": 50,
  "successful_predictions": 46,
  "failed_predictions": 4,
  "certificate_path": "reports/certificates/cert_eval_20251127_174000.pdf",
  "report_path": "reports/evaluations/report_eval_20251127_174000.json",
  "timestamp": "2025-11-27T17:42:00"
}
```

#### `GET /certificate/{evaluation_id}`
Download PDF certificate.

**Response**: PDF file download

#### `GET /report/{evaluation_id}`
Download JSON report.

**Response**: JSON file download

---

### Management

#### `GET /evaluations`
List all evaluations.

**Response**:
```json
{
  "evaluations": [
    {
      "evaluation_id": "eval_001",
      "status": "completed",
      "model_name": "Model_v1",
      "started_at": "2025-11-27T17:40:00",
      "completed_at": "2025-11-27T17:42:00"
    }
  ],
  "total": 1
}
```

#### `DELETE /evaluations/{evaluation_id}`
Delete an evaluation and its results.

**Response**:
```json
{
  "message": "Evaluation eval_001 deleted successfully"
}
```

#### `POST /config`
Update agent configuration.

**Request**:
```json
{
  "model_endpoint_url": "http://localhost:8000/predict",
  "max_test_cases": 100
}
```

**Response**:
```json
{
  "message": "Configuration updated successfully",
  "config": {...}
}
```

---

## Usage Examples

### Python Client Example

```python
import requests
import time

# 1. Start evaluation
response = requests.post("http://localhost:8001/evaluate", json={
    "test_data_path": "data/test/benchmark.jsonl",
    "model_endpoint_url": "http://localhost:8000/predict",
    "model_name": "MyModel_v1"
})

eval_id = response.json()["evaluation_id"]
print(f"Evaluation started: {eval_id}")

# 2. Poll status
while True:
    status_response = requests.get(f"http://localhost:8001/status/{eval_id}")
    status = status_response.json()["status"]
    
    print(f"Status: {status}")
    
    if status in ["completed", "failed"]:
        break
    
    time.sleep(5)

# 3. Get results
if status == "completed":
    results = requests.get(f"http://localhost:8001/results/{eval_id}")
    print(results.json())
    
    # 4. Download certificate
    cert = requests.get(f"http://localhost:8001/certificate/{eval_id}")
    with open(f"certificate_{eval_id}.pdf", "wb") as f:
        f.write(cert.content)
```

### cURL Examples

```bash
# Start evaluation
curl -X POST http://localhost:8001/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "test_data_path": "data/test/benchmark.jsonl",
    "model_endpoint_url": "http://localhost:8000/predict",
    "model_name": "MyModel"
  }'

# Check status
curl http://localhost:8001/status/eval_20251127_174000

# Get results
curl http://localhost:8001/results/eval_20251127_174000

# Download certificate
curl -O http://localhost:8001/certificate/eval_20251127_174000

# List all evaluations
curl http://localhost:8001/evaluations
```

---

## Architecture

```
┌──────────────┐
│   Client     │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────────┐
│  FastAPI Server  │
│  (api.py)        │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  MedAgentBench   │
│  (agent.py)      │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ LangGraph        │
│ Workflow         │
└──────────────────┘
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200` - Success
- `400` - Bad request
- `404` - Resource not found
- `503` - Service unavailable

**Error Response Format**:
```json
{
  "detail": "Error message"
}
```

---

## Production Deployment

For production, consider:

1. **Database**: Replace in-memory storage with PostgreSQL/MongoDB
2. **Authentication**: Add API key or OAuth authentication
3. **Rate Limiting**: Implement rate limiting
4. **CORS**: Configure CORS for frontend access
5. **HTTPS**: Use SSL/TLS certificates
6. **Monitoring**: Add Prometheus/Grafana monitoring
7. **Load Balancing**: Use Nginx or cloud load balancer

### Docker Deployment

```bash
# Create Dockerfile in agent_3_benchmark/
docker build -t medagentbench-api .
docker run -p 8001:8001 medagentbench-api
```

---

**Status**: ✅ Ready for use  
**Version**: 1.0.0  
**Last Updated**: November 27, 2025
