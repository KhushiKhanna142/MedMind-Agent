"""
State management for MedAgentBench workflow
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class EvaluationState:
    """
    State object for evaluation workflow
    """
    
    # Workflow tracking
    status: str = "initialized"
    current_step: str = ""
    error: Optional[str] = None
    
    # Test data
    test_data_path: Optional[str] = None
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    total_test_cases: int = 0
    loaded_test_cases: int = 0
    
    # Model configuration
    model_endpoint_url: Optional[str] = None
    model_endpoint_type: str = "fastapi"
    
    # Evaluation results
    predictions: List[Dict[str, Any]] = field(default_factory=list)
    ground_truth: List[Dict[str, Any]] = field(default_factory=list)
    evaluation_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    safety_score: float = 0.0
    hallucination_score: float = 1.0
    unsafe_responses: int = 0
    
    # Safety evaluation
    safety_evaluation: Dict[str, Any] = field(default_factory=dict)
    safety_issues: List[Dict[str, Any]] = field(default_factory=list)
    
    # Domain-specific metrics
    domain_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Pass/Fail evaluation
    pass_fail_result: Dict[str, Any] = field(default_factory=dict)
    evaluation_status: str = "PENDING"  # PENDING, PASS, FAIL
    
    # Report generation
    certificate_path: Optional[str] = None
    report_path: Optional[str] = None
    certificate_generated: bool = False
    
    # Metadata
    evaluation_id: Optional[str] = None
    model_name: Optional[str] = None
    evaluation_timestamp: Optional[str] = None
    evaluation_duration: Optional[float] = None
    
    # Error tracking
    failed_cases: List[int] = field(default_factory=list)
    error_details: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvaluationState":
        """Create state from dictionary"""
        # Remove None values and convert appropriately
        cleaned_data = {k: v for k, v in data.items() if v is not None}
        return cls(**cleaned_data)
    
    def update_metrics(self, metrics: Dict[str, float]):
        """Update metrics in state"""
        self.metrics.update(metrics)
        
        # Update individual metric fields
        self.accuracy = metrics.get("accuracy", self.accuracy)
        self.precision = metrics.get("precision", self.precision)
        self.recall = metrics.get("recall", self.recall)
        self.f1_score = metrics.get("f1_score", self.f1_score)
        self.safety_score = metrics.get("safety_score", self.safety_score)
        self.hallucination_score = metrics.get("hallucination_score", self.hallucination_score)
        self.unsafe_responses = int(metrics.get("unsafe_responses", self.unsafe_responses))
    
    def update_status(self, status: str, step: str = ""):
        """Update workflow status"""
        self.status = status
        self.current_step = step
        if not self.evaluation_timestamp:
            self.evaluation_timestamp = datetime.now().isoformat()
    
    def mark_completed(self):
        """Mark evaluation as completed"""
        self.status = "completed"
        self.current_step = "completed"
        if not self.evaluation_timestamp:
            self.evaluation_timestamp = datetime.now().isoformat()
    
    def mark_failed(self, error: str):
        """Mark evaluation as failed"""
        self.status = "failed"
        self.error = error
        self.evaluation_status = "FAIL"


def create_initial_state(
    test_data_path: str,
    model_endpoint_url: str,
    model_endpoint_type: str = "fastapi",
    evaluation_id: Optional[str] = None,
    model_name: Optional[str] = None
) -> EvaluationState:
    """
    Create initial evaluation state
    
    Args:
        test_data_path: Path to test JSONL file
        model_endpoint_url: Model endpoint URL
        model_endpoint_type: Type of endpoint (fastapi, vertex_ai, etc.)
        evaluation_id: Optional evaluation ID
        model_name: Optional model name
        
    Returns:
        Initialized EvaluationState
    """
    if not evaluation_id:
        evaluation_id = f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    state = EvaluationState(
        status="initialized",
        test_data_path=test_data_path,
        model_endpoint_url=model_endpoint_url,
        model_endpoint_type=model_endpoint_type,
        evaluation_id=evaluation_id,
        model_name=model_name,
        evaluation_timestamp=datetime.now().isoformat()
    )
    
    return state

