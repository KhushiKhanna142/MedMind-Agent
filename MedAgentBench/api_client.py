"""
Test client for MedAgentBench API

This script demonstrates how to use the MedAgentBench API programmatically.
"""

import requests
import time
import json
from typing import Dict, Any


class MedAgentBenchClient:
    """Client for interacting with MedAgentBench API"""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize client
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def start_evaluation(
        self,
        test_data_path: str,
        model_endpoint_url: str,
        model_name: str = None,
        model_endpoint_type: str = "fastapi",
        max_test_cases: int = None
    ) -> str:
        """
        Start a new evaluation
        
        Args:
            test_data_path: Path to test JSONL file
            model_endpoint_url: Model endpoint URL
            model_name: Name of the model
            model_endpoint_type: Type of endpoint
            max_test_cases: Max test cases to evaluate
            
        Returns:
            Evaluation ID
        """
        payload = {
            "test_data_path": test_data_path,
            "model_endpoint_url": model_endpoint_url,
            "model_endpoint_type": model_endpoint_type
        }
        
        if model_name:
            payload["model_name"] = model_name
        if max_test_cases:
            payload["max_test_cases"] = max_test_cases
        
        response = requests.post(f"{self.base_url}/evaluate", json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result["evaluation_id"]
    
    def get_status(self, evaluation_id: str) -> Dict[str, Any]:
        """
        Get evaluation status
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            Status information
        """
        response = requests.get(f"{self.base_url}/status/{evaluation_id}")
        response.raise_for_status()
        return response.json()
    
    def get_results(self, evaluation_id: str) -> Dict[str, Any]:
        """
        Get evaluation results
        
        Args:
            evaluation_id: Evaluation ID
            
        Returns:
            Evaluation results
        """
        response = requests.get(f"{self.base_url}/results/{evaluation_id}")
        response.raise_for_status()
        return response.json()
    
    def download_certificate(self, evaluation_id: str, output_path: str):
        """
        Download PDF certificate
        
        Args:
            evaluation_id: Evaluation ID
            output_path: Path to save certificate
        """
        response = requests.get(f"{self.base_url}/certificate/{evaluation_id}")
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Certificate saved to {output_path}")
    
    def download_report(self, evaluation_id: str, output_path: str):
        """
        Download JSON report
        
        Args:
            evaluation_id: Evaluation ID
            output_path: Path to save report
        """
        response = requests.get(f"{self.base_url}/report/{evaluation_id}")
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        
        print(f"✅ Report saved to {output_path}")
    
    def list_evaluations(self) -> Dict[str, Any]:
        """List all evaluations"""
        response = requests.get(f"{self.base_url}/evaluations")
        response.raise_for_status()
        return response.json()
    
    def delete_evaluation(self, evaluation_id: str):
        """
        Delete an evaluation
        
        Args:
            evaluation_id: Evaluation ID
        """
        response = requests.delete(f"{self.base_url}/evaluations/{evaluation_id}")
        response.raise_for_status()
        return response.json()
    
    def wait_for_completion(
        self,
        evaluation_id: str,
        poll_interval: int = 5,
        timeout: int = 3600
    ) -> Dict[str, Any]:
        """
        Wait for evaluation to complete
        
        Args:
            evaluation_id: Evaluation ID
            poll_interval: Seconds between status checks
            timeout: Maximum seconds to wait
            
        Returns:
            Final status
        """
        start_time = time.time()
        
        while True:
            status = self.get_status(evaluation_id)
            current_status = status["status"]
            
            print(f"Status: {current_status}")
            
            if current_status in ["completed", "failed"]:
                return status
            
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Evaluation {evaluation_id} timed out after {timeout}s")
            
            time.sleep(poll_interval)


def example_usage():
    """Example usage of the client"""
    print("=" * 80)
    print("MedAgentBench API Client - Example Usage")
    print("=" * 80)
    print()
    
    # Initialize client
    client = MedAgentBenchClient()
    
    # 1. Health check
    print("Step 1: Health Check")
    health = client.health_check()
    print(f"✅ API Status: {health['status']}")
    print()
    
    # 2. Start evaluation
    print("Step 2: Starting Evaluation")
    eval_id = client.start_evaluation(
        test_data_path="data/test/sample_benchmark.jsonl",
        model_endpoint_url="http://localhost:8000/predict",
        model_name="TestModel_v1",
        max_test_cases=10
    )
    print(f"✅ Evaluation started: {eval_id}")
    print()
    
    # 3. Wait for completion
    print("Step 3: Waiting for Completion")
    final_status = client.wait_for_completion(eval_id, poll_interval=5)
    print(f"✅ Final status: {final_status['status']}")
    print()
    
    # 4. Get results
    if final_status['status'] == "completed":
        print("Step 4: Retrieving Results")
        results = client.get_results(eval_id)
        
        print(f"Model: {results['model_name']}")
        print(f"Status: {results['evaluation_status']}")
        print(f"Accuracy: {results['metrics'].get('accuracy', 0):.3f}")
        print(f"F1 Score: {results['metrics'].get('f1_score', 0):.3f}")
        print(f"Safety Score: {results['safety_score']:.3f}")
        print()
        
        # 5. Download certificate
        print("Step 5: Downloading Certificate")
        client.download_certificate(eval_id, f"certificate_{eval_id}.pdf")
        print()
        
        # 6. Download report
        print("Step 6: Downloading Report")
        client.download_report(eval_id, f"report_{eval_id}.json")
        print()
    
    # 7. List all evaluations
    print("Step 7: Listing All Evaluations")
    all_evals = client.list_evaluations()
    print(f"Total evaluations: {all_evals['total']}")
    print()
    
    print("=" * 80)
    print("✅ Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        example_usage()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
