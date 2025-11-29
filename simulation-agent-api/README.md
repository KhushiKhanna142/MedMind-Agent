# Simulation Agent API

A focused REST API for testing and evaluating medical AI models through clinical simulations.

## 🚀 Quick Start

### Local Development
```bash
pip install -r requirements-api.txt
python run_api.py
```

Visit: http://localhost:8000/docs

### Cloud Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## 📡 API Endpoints

- `GET /api/simulation/health` - Health check
- `POST /api/simulation/generate-questions` - Generate clinical questions
- `POST /api/simulation/load-benchmarks` - Load benchmark answers
- `POST /api/simulation/compare-answers` - Compare model vs benchmark answers
- `POST /api/simulation/run` - Run complete simulation workflow

## 📁 Project Structure

```
simulation-agent-api/
├── agents/                    # Agent implementations
│   ├── agent_2_simulation/   # Core simulation agent
│   ├── base/                 # Base agent classes
│   └── shared/               # Shared utilities
├── src/                      # API source code
│   ├── api/                  # FastAPI routes and schemas
│   ├── config/               # Configuration
│   ├── database/             # Database models
│   ├── models/               # Data models
│   ├── services/             # Business logic
│   └── utils/                # Utilities
├── run_api.py               # API launcher
└── requirements-api.txt     # Dependencies
```

## 📚 Documentation

- **Usage Guide**: [API_USAGE.md](API_USAGE.md)
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Interactive Docs**: http://localhost:8000/docs (when running)

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Validation**: Pydantic v2
- **Python**: 3.11+

## 📄 License

MIT

