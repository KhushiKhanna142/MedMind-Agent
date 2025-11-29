# MedAgentBench API

🏥 **Medical AI Model Evaluation Agent with REST API**

LangGraph-based evaluation agent that provides comprehensive assessment of medical AI models through a FastAPI REST interface.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6.8-orange.svg)](https://github.com/langchain-ai/langgraph)

## ✨ Features

- 🔄 **LangGraph Workflow** - State-based evaluation orchestration
- 🌐 **REST API** - 12 FastAPI endpoints for easy integration
- 📊 **Comprehensive Metrics** - Accuracy, F1, Precision, Recall, Safety Score
- 📄 **PDF Certificates** - Professional evaluation certificates
- 🔒 **Safety Evaluation** - Medical safety and hallucination detection
- 🚀 **Async Processing** - Background task evaluation
- 📦 **Python Client** - Ready-to-use client library

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r api_requirements.txt

# Start API server
uvicorn api:app --host 0.0.0.0 --port 8001 --reload

# Visit Swagger UI
open http://localhost:8001/docs
```

## 💻 Usage Example

```python
from api_client import MedAgentBenchClient

client = MedAgentBenchClient("http://localhost:8001")

# Start evaluation
eval_id = client.start_evaluation(
    test_data_path="data/test/benchmark.jsonl",
    model_endpoint_url="http://your-model:8000/predict",
    model_name="MyMedicalModel_v1"
)

# Get results
results = client.get_results(eval_id)
print(f"Status: {results['evaluation_status']}")
print(f"F1 Score: {results['metrics']['f1_score']:.3f}")
```

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/evaluate` | POST | Start evaluation |
| `/status/{id}` | GET | Check status |
| `/results/{id}` | GET | Get results |
| `/certificate/{id}` | GET | Download PDF |
| `/health` | GET | Health check |

[See complete API documentation →](API_GUIDE.md)

## 📊 Evaluation Metrics

- **Accuracy** - Overall correctness
- **Precision/Recall/F1** - Performance metrics
- **Safety Score** - Medical safety assessment
- **Hallucination Score** - Confidence calibration

## 🔗 Integration

Perfect for Vertex AI and other ML platforms:

```python
# Evaluate Vertex AI model
eval_id = client.start_evaluation(
    test_data_path="gs://bucket/test.jsonl",
    model_endpoint_url="https://vertex-endpoint/predict",
    model_endpoint_type="vertex_ai"
)
```

[Integration Guide →](INTEGRATION_FOR_VERTEX_AI.md)

## 📋 Requirements

- Python 3.9+
- FastAPI
- LangGraph
- Pydantic v2

## 📖 Documentation

- [API Guide](API_GUIDE.md) - Complete API reference
- [Vertex AI Integration](INTEGRATION_FOR_VERTEX_AI.md) - Integration guide
- [LangGraph Details](LANGGRAPH_CONVERSION.md) - Technical details

## 🐳 Docker

```bash
docker build -t medagentbench-api .
docker run -p 8001:8001 medagentbench-api
```

## 📄 License

MIT License

---

**Part of MedAgent Suite** - Multi-agent medical AI platform
