"""
Tool: Run inference on model endpoint for test cases
"""

import logging
import requests
import json
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)


class ModelRunner:
    """
    Run inference requests against model endpoint
    """
    
    def __init__(self, config=None):
        """
        Initialize Model Runner
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.endpoint_url = config.model_endpoint_url if config else ""
        self.endpoint_type = config.model_endpoint_type if config else "fastapi"
        self.api_key = config.model_api_key if config else None
        self.timeout = config.request_timeout if config else 30
        self.max_workers = config.max_workers if config else 5
        
        logger.info(f"ModelRunner initialized with endpoint: {self.endpoint_url}")
    
    def run_inference(
        self,
        test_cases: List[Dict[str, Any]],
        parallel: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run inference on all test cases
        
        Args:
            test_cases: List of test case dictionaries
            parallel: Whether to run requests in parallel
            
        Returns:
            List of prediction dictionaries
        """
        logger.info(f"Running inference on {len(test_cases)} test cases")
        
        if parallel and len(test_cases) > 1:
            predictions = self._run_parallel(test_cases)
        else:
            predictions = self._run_sequential(test_cases)
        
        logger.info(f"✅ Completed inference for {len(predictions)} cases")
        return predictions
    
    def _run_parallel(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run inference requests in parallel"""
        predictions = []
        failed_cases = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_case = {
                executor.submit(self._run_single_inference, case): case
                for case in test_cases
            }
            
            for future in as_completed(future_to_case):
                case = future_to_case[future]
                try:
                    result = future.result()
                    predictions.append(result)
                except Exception as e:
                    logger.error(f"Failed inference for case {case.get('case_id')}: {e}")
                    failed_cases.append({
                        "case_id": case.get("case_id"),
                        "error": str(e)
                    })
                    # Add failed prediction placeholder
                    predictions.append({
                        "case_id": case.get("case_id"),
                        "prediction": None,
                        "error": str(e),
                        "success": False
                    })
        
        if failed_cases:
            logger.warning(f"Failed {len(failed_cases)} inference requests")
        
        return predictions
    
    def _run_sequential(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Run inference requests sequentially"""
        predictions = []
        
        for i, case in enumerate(test_cases):
            try:
                result = self._run_single_inference(case)
                predictions.append(result)
                
                # Progress logging
                if (i + 1) % 10 == 0:
                    logger.info(f"Processed {i + 1}/{len(test_cases)} cases")
                
                # Small delay to avoid rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed inference for case {case.get('case_id')}: {e}")
                predictions.append({
                    "case_id": case.get("case_id"),
                    "prediction": None,
                    "error": str(e),
                    "success": False
                })
        
        return predictions
    
    def _run_single_inference(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run inference for a single test case
        
        Args:
            test_case: Test case dictionary
            
        Returns:
            Prediction dictionary
        """
        case_id = test_case.get("case_id", "unknown")
        input_data = test_case.get("input", {})
        
        try:
            if self.endpoint_type == "fastapi":
                response = self._call_fastapi_endpoint(input_data)
            elif self.endpoint_type == "vertex_ai":
                response = self._call_vertex_ai_endpoint(input_data)
            else:
                response = self._call_custom_endpoint(input_data)
            
            return {
                "case_id": case_id,
                "prediction": response.get("prediction") or response.get("output") or response,
                "confidence": response.get("confidence"),
                "metadata": response.get("metadata", {}),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Inference error for case {case_id}: {e}")
            raise
    
    def _call_fastapi_endpoint(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call FastAPI endpoint"""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Use endpoint_url directly if it already includes the path, otherwise append /predict
        url = self.endpoint_url
        if not url.endswith("/predict") and not url.endswith("/predict/"):
            url = f"{url.rstrip('/')}/predict"
        
        response = requests.post(
            url,
            json={"input": input_data},
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def _call_vertex_ai_endpoint(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call Vertex AI endpoint"""
        try:
            from google.cloud import aiplatform
            
            # This would need proper Vertex AI endpoint configuration
            # Placeholder implementation
            headers = {"Content-Type": "application/json"}
            
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = requests.post(
                self.endpoint_url,
                json={"instances": [input_data]},
                headers=headers,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract predictions from Vertex AI response format
            if "predictions" in result and len(result["predictions"]) > 0:
                return result["predictions"][0]
            
            return result
            
        except ImportError:
            logger.warning("google-cloud-aiplatform not installed, falling back to HTTP")
            return self._call_fastapi_endpoint(input_data)
    
    def _call_custom_endpoint(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call custom endpoint format"""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        response = requests.post(
            self.endpoint_url,
            json=input_data,
            headers=headers,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()

