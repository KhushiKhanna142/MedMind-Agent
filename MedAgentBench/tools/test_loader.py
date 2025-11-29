"""
Tool: Load test JSONL tasks for evaluation
"""

import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from google.cloud import storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    storage = None

logger = logging.getLogger(__name__)


class TestLoader:
    """
    Load test cases from JSONL files for evaluation
    """
    
    def __init__(self, config=None):
        """
        Initialize Test Loader
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.gcs_client = None
        
        if config and config.gcs_bucket and GCS_AVAILABLE:
            try:
                self.gcs_client = storage.Client()
                logger.info("GCS client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize GCS client: {e}")
                self.gcs_client = None
        elif config and config.gcs_bucket and not GCS_AVAILABLE:
            logger.warning("GCS bucket specified but google-cloud-storage not installed")
            self.gcs_client = None
        
        logger.info("TestLoader initialized")
    
    def load(
        self,
        test_data_path: str,
        max_cases: Optional[int] = None,
        format: str = "jsonl"
    ) -> List[Dict[str, Any]]:
        """
        Load test cases from file
        
        Args:
            test_data_path: Path to test data file (local or GCS)
            max_cases: Maximum number of cases to load (None = all)
            format: File format (jsonl, json)
            
        Returns:
            List of test case dictionaries
        """
        logger.info(f"Loading test data from: {test_data_path}")
        
        try:
            # Check if GCS path
            if test_data_path.startswith("gs://"):
                test_cases = self._load_from_gcs(test_data_path, max_cases, format)
            else:
                test_cases = self._load_from_local(test_data_path, max_cases, format)
            
            logger.info(f"✅ Loaded {len(test_cases)} test cases successfully")
            return test_cases
            
        except Exception as e:
            logger.error(f"❌ Failed to load test data: {e}")
            raise
    
    def _load_from_local(
        self,
        file_path: str,
        max_cases: Optional[int],
        format: str
    ) -> List[Dict[str, Any]]:
        """Load test cases from local file"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Test data file not found: {file_path}")
        
        test_cases = []
        
        if format.lower() == "jsonl":
            with open(path, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f):
                    if max_cases and i >= max_cases:
                        break
                    
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        case = json.loads(line)
                        test_cases.append(case)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Skipping invalid JSON line {i+1}: {e}")
                        continue
        
        elif format.lower() == "json":
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if isinstance(data, list):
                    test_cases = data[:max_cases] if max_cases else data
                elif isinstance(data, dict):
                    # Assume dict contains a 'test_cases' key
                    test_cases = data.get("test_cases", [])
                    if max_cases:
                        test_cases = test_cases[:max_cases]
        
        return test_cases
    
    def _load_from_gcs(
        self,
        gcs_path: str,
        max_cases: Optional[int],
        format: str
    ) -> List[Dict[str, Any]]:
        """Load test cases from GCS"""
        if not GCS_AVAILABLE:
            raise ImportError("google-cloud-storage is required for GCS support. Install with: pip install google-cloud-storage")
        if not self.gcs_client:
            raise RuntimeError("GCS client not initialized")
        
        # Parse GCS path: gs://bucket/path/to/file.jsonl
        parts = gcs_path.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1] if len(parts) > 1 else ""
        
        bucket = self.gcs_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        test_cases = []
        
        if format.lower() == "jsonl":
            content = blob.download_as_text()
            for i, line in enumerate(content.splitlines()):
                if max_cases and i >= max_cases:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    case = json.loads(line)
                    test_cases.append(case)
                except json.JSONDecodeError as e:
                    logger.warning(f"Skipping invalid JSON line {i+1}: {e}")
                    continue
        
        elif format.lower() == "json":
            content = blob.download_as_text()
            data = json.loads(content)
            
            if isinstance(data, list):
                test_cases = data[:max_cases] if max_cases else data
            elif isinstance(data, dict):
                test_cases = data.get("test_cases", [])
                if max_cases:
                    test_cases = test_cases[:max_cases]
        
        return test_cases
    
    def validate_test_case(self, test_case: Dict[str, Any]) -> bool:
        """
        Validate a test case has required fields
        
        Args:
            test_case: Test case dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["case_id", "input"]
        
        for field in required_fields:
            if field not in test_case:
                logger.warning(f"Test case missing required field: {field}")
                return False
        
        return True
    
    def extract_ground_truth(self, test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract ground truth labels from test cases
        
        Args:
            test_cases: List of test case dictionaries
            
        Returns:
            List of ground truth dictionaries
        """
        ground_truth = []
        
        for case in test_cases:
            gt = {
                "case_id": case.get("case_id"),
                "expected_output": case.get("expected_output"),
                "expected_label": case.get("expected_label"),
                "expected_class": case.get("expected_class"),
                "metadata": case.get("metadata", {})
            }
            ground_truth.append(gt)
        
        return ground_truth

