import requests
import json

url = "http://127.0.0.1:8000/run/sft"

payload = {
    "model_id": "meta/llama3_1@llama-3.1-8b",
    "dataset_path": "data.jsonl",
    "epochs": 3,
    "tuned_model_display_name": "output"
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
