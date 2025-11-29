# Simulation Agent API - Usage Guide

Welcome to the **Simulation Agent API**! This REST API allows you to test and evaluate medical AI models through clinical simulations.

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to the backend directory
cd c:\Users\aksha\backend

# Install dependencies
pip install -r requirements-api.txt
```

### 2. Start the API Server

```bash
# Run the API server
python run_api.py
```

The API will start on `http://localhost:8000`

### 3. Access Interactive Documentation

Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Health Check
```bash
GET /api/simulation/health
```

**Example:**
```bash
curl http://localhost:8000/api/simulation/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "agent": "Simulation Agent",
  "message": "API is running successfully"
}
```

---

### Generate Questions
```bash
POST /api/simulation/generate-questions
```

Generate clinical simulation questions for testing.

**Request Body:**
```json
{
  "num_questions": 10,
  "difficulty": "varied",
  "domains": ["cardiology", "neurology"],
  "model_type": "general"
}
```

**Example (curl):**
```bash
curl -X POST http://localhost:8000/api/simulation/generate-questions \
  -H "Content-Type: application/json" \
  -d "{\"num_questions\": 5, \"difficulty\": \"easy\", \"domains\": [\"cardiology\"]}"
```

**Example (Python):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/simulation/generate-questions",
    json={
        "num_questions": 10,
        "difficulty": "varied",
        "domains": ["cardiology", "emergency_medicine"],
        "model_type": "general"
    }
)

questions = response.json()
print(f"Generated {questions['count']} questions")
```

---

### Load Benchmark Answers
```bash
POST /api/simulation/load-benchmarks
```

Load correct answers for questions.

**Request Body:**
```json
{
  "questions": [
    {
      "question_id": "Q001",
      "question_text": "Sample question?",
      "correct_answer": "A) Option A"
    }
  ],
  "source": "auto"
}
```

---

### Compare Answers
```bash
POST /api/simulation/compare-answers
```

Compare model answers with benchmark answers.

**Request Body:**
```json
{
  "model_answers": ["A) Option A", "B) Option B"],
  "benchmark_answers": ["A) Option A", "C) Option C"],
  "questions": [
    {"question_id": "Q001", "domain": "cardiology", "difficulty": "easy"},
    {"question_id": "Q002", "domain": "neurology", "difficulty": "medium"}
  ]
}
```

**Example (Python):**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/simulation/compare-answers",
    json={
        "model_answers": ["A) Anterior STEMI", "B) Increase diuretic dose"],
        "benchmark_answers": ["B) Anterior STEMI", "B) Increase diuretic dose"],
        "questions": [
            {"question_id": "Q001", "domain": "cardiology", "difficulty": "easy"},
            {"question_id": "Q002", "domain": "cardiology", "difficulty": "medium"}
        ]
    }
)

results = response.json()
print(f"Accuracy: {results['accuracy']:.2%}")
print(f"Correct: {results['correct_count']}/{results['total_count']}")
```

---

### Run Complete Simulation
```bash
POST /api/simulation/run
```

Execute a complete simulation workflow with question generation, benchmark loading, and optional answer comparison.

**Request Body:**
```json
{
  "num_questions": 20,
  "difficulty": "varied",
  "domains": ["cardiology", "emergency_medicine"],
  "model_type": "general",
  "model_name": "MedLM-v1",
  "model_answers": ["A) Option A", "B) Option B", ...]
}
```

**Example (Python):**
```python
import requests

# Run simulation without model answers (just generate questions)
response = requests.post(
    "http://localhost:8000/api/simulation/run",
    json={
        "num_questions": 20,
        "difficulty": "varied",
        "domains": ["cardiology", "neurology"],
        "model_type": "general",
        "model_name": "TestModel-v1"
    }
)

simulation = response.json()
print(f"Session ID: {simulation['session_id']}")
print(f"Generated {len(simulation['questions'])} questions")

# Extract questions and benchmark answers
questions = simulation['questions']
benchmark_answers = simulation['benchmark_answers']

# TODO: Run your model to get answers
# model_answers = your_model.predict(questions)

# Run simulation WITH model answers for evaluation
response = requests.post(
    "http://localhost:8000/api/simulation/run",
    json={
        "num_questions": 20,
        "difficulty": "varied",
        "domains": ["cardiology"],
        "model_type": "general",
        "model_name": "TestModel-v1",
        "model_answers": model_answers  # Your model's answers
    }
)

results = response.json()
print(f"Accuracy: {results['simulation_accuracy']:.2%}")
print(f"Passed: {results['simulation_passed']}")

if results['error_analysis']:
    print("\nError Analysis:")
    for suggestion in results['error_analysis']['improvement_suggestions']:
        print(f"  - {suggestion}")
```

---

## 🌐 Sharing with Your Friend

### Option 1: Local Network Access

If your friend is on the same network:

1. Find your local IP address:
```bash
ipconfig  # On Windows
```

2. Share the URL with your friend:
```
http://YOUR_IP_ADDRESS:8000
```

### Option 2: Using ngrok (Internet Access)

To share over the internet:

1. Install ngrok: https://ngrok.com/download

2. Start the API server:
```bash
python run_api.py
```

3. In a new terminal, run ngrok:
```bash
ngrok http 8000
```

4. Share the ngrok URL (e.g., `https://abc123.ngrok.io`) with your friend

### Option 3: Deploy to Cloud

Deploy to platforms like:
- **Render**: https://render.com
- **Railway**: https://railway.app
- **Heroku**: https://heroku.com
- **Google Cloud Run**
- **AWS Lambda**

---

## 📊 Response Formats

### Simulation Response (Full)

```json
{
  "session_id": "uuid-here",
  "status": "completed",
  "questions": [...],
  "benchmark_answers": [...],
  "model_answers": [...],
  "comparison_results": {
    "accuracy": 0.85,
    "correct_count": 17,
    "incorrect_count": 3,
    "total_count": 20,
    "detailed_comparisons": [...]
  },
  "metrics": {
    "accuracy": 0.85,
    "accuracy_by_domain": {
      "cardiology": 0.9,
      "neurology": 0.8
    },
    "accuracy_by_difficulty": {
      "easy": 0.95,
      "medium": 0.85,
      "hard": 0.7
    }
  },
  "error_analysis": {
    "total_errors": 3,
    "error_types": {...},
    "error_examples": [...],
    "improvement_suggestions": [
      "Focus on improving neurology domain knowledge",
      "Performance on hard questions is weak"
    ]
  },
  "simulation_passed": true,
  "simulation_accuracy": 0.85,
  "message": "Simulation completed successfully",
  "warnings": [],
  "errors": []
}
```

---

## 🔧 Configuration

### Change Port

Edit `run_api.py` and modify:
```python
port=8000  # Change to your desired port
```

### Disable Auto-Reload

For production, set:
```python
reload=False
```

### Enable HTTPS

Use a reverse proxy like nginx or deploy to a platform that provides HTTPS.

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Windows: Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Import Errors
Make sure you're in the backend directory and have installed dependencies:
```bash
cd c:\Users\aksha\backend
pip install -r requirements-api.txt
```

### CORS Issues
The API allows all origins by default. If you need to restrict:

Edit `src/api/simulation_api.py`:
```python
allow_origins=["http://localhost:3000", "https://yourapp.com"]
```

---

## 📚 Additional Resources

- **Interactive Docs**: http://localhost:8000/docs
- **API Schema**: http://localhost:8000/openapi.json
- **Health Check**: http://localhost:8000/api/simulation/health

---

## 💡 Example Workflow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Generate questions
questions_response = requests.post(
    f"{BASE_URL}/api/simulation/generate-questions",
    json={"num_questions": 10, "difficulty": "varied", "domains": ["cardiology"]}
)
questions = questions_response.json()["questions"]

# 2. Get your model's answers (implement your model here)
model_answers = []
for q in questions:
    # answer = your_model.predict(q["question_text"])
    answer = "A) Sample answer"  # Placeholder
    model_answers.append(answer)

# 3. Run full simulation with evaluation
simulation_response = requests.post(
    f"{BASE_URL}/api/simulation/run",
    json={
        "questions": questions,
        "model_answers": model_answers,
        "model_name": "MyModel-v1"
    }
)

results = simulation_response.json()
print(f"Accuracy: {results['simulation_accuracy']:.2%}")
print(f"Passed: {results['simulation_passed']}")
```

---

Happy Testing! 🎉
