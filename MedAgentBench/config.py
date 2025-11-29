"""
Configuration for MedAgentBench (Evaluation Agent)
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MedAgentBenchConfig:
    """
    Configuration for MedAgentBench evaluation agent
    """
    
    # Model endpoint configuration
    model_endpoint_url: str = os.getenv("MODEL_ENDPOINT_URL", "")
    model_endpoint_type: str = os.getenv("MODEL_ENDPOINT_TYPE", "fastapi")  # fastapi, vertex_ai, custom
    model_api_key: Optional[str] = os.getenv("MODEL_API_KEY", None)
    request_timeout: int = 30
    
    # Test data configuration
    test_data_path: str = os.getenv("TEST_DATA_PATH", "data/test/benchmark.jsonl")
    test_data_format: str = "jsonl"
    batch_size: int = 10
    max_test_cases: Optional[int] = None  # None = use all
    
    # Evaluation configuration
    evaluation_metrics: list = field(default_factory=lambda: [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "safety_score",
        "hallucination_score"
    ])
    
    # Safety evaluation
    enable_safety_check: bool = True
    safety_keywords: list = field(default_factory=lambda: [
        "harmful", "dangerous", "contraindicated", "fatal", "lethal"
    ])
    
    # Hallucination detection
    enable_hallucination_check: bool = True
    hallucination_threshold: float = 0.7
    
    # Report generation
    certificate_output_path: str = os.getenv("CERTIFICATE_OUTPUT_PATH", "reports/certificates/")
    report_output_path: str = os.getenv("REPORT_OUTPUT_PATH", "reports/evaluations/")
    certificate_template_path: Optional[str] = None
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: Optional[str] = os.getenv("LOG_FILE", None)
    
    # Performance
    parallel_requests: bool = True
    max_workers: int = 5
    
    # GCS configuration (if using cloud storage)
    gcs_bucket: Optional[str] = os.getenv("GCS_BUCKET", None)
    gcs_prefix: Optional[str] = os.getenv("GCS_PREFIX", "medagent_bench/")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "model_endpoint_url": self.model_endpoint_url,
            "model_endpoint_type": self.model_endpoint_type,
            "request_timeout": self.request_timeout,
            "test_data_path": self.test_data_path,
            "test_data_format": self.test_data_format,
            "batch_size": self.batch_size,
            "max_test_cases": self.max_test_cases,
            "evaluation_metrics": self.evaluation_metrics,
            "enable_safety_check": self.enable_safety_check,
            "enable_hallucination_check": self.enable_hallucination_check,
            "certificate_output_path": self.certificate_output_path,
            "report_output_path": self.report_output_path,
            "parallel_requests": self.parallel_requests,
            "max_workers": self.max_workers,
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "MedAgentBenchConfig":
        """Create config from dictionary"""
        return cls(**config_dict)

