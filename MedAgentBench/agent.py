"""
MedAgentBench - Evaluation Agent
Main agent class for coordinating model evaluation
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from config import MedAgentBenchConfig
from thresholds import EvaluationThresholds, DEFAULT_THRESHOLDS
from graph.workflow import create_workflow
from tools.test_loader import TestLoader
from tools.model_runner import ModelRunner
from tools.metrics_calculator import MetricsCalculator
from tools.safety_evaluator import SafetyEvaluator
from tools.report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class MedAgentBench:
    """
    MedAgentBench - Evaluation Agent for Medical AI Models
    
    This agent:
    1. Loads test JSONL tasks
    2. Sends each case to the model endpoint
    3. Computes accuracy, precision, recall, F1, safety score, hallucination score
    4. Generates a professional evaluation certificate (PDF)
    5. Outputs a final "PASS / FAIL" rating for the model
    """
    
    def __init__(self, config: Optional[MedAgentBenchConfig] = None):
        """
        Initialize MedAgentBench
        
        Args:
            config: Configuration object (optional)
        """
        self.config = config or MedAgentBenchConfig()
        self.thresholds = DEFAULT_THRESHOLDS
        
        # Initialize tools
        logger.info("Initializing MedAgentBench tools...")
        self.test_loader = TestLoader(config=self.config)
        self.model_runner = ModelRunner(config=self.config)
        self.metrics_calculator = MetricsCalculator(config=self.config)
        self.safety_evaluator = SafetyEvaluator(config=self.config)
        self.report_generator = ReportGenerator(config=self.config)
        
        # Create workflow
        self.workflow = create_workflow(
            test_loader=self.test_loader,
            model_runner=self.model_runner,
            metrics_calculator=self.metrics_calculator,
            safety_evaluator=self.safety_evaluator,
            report_generator=self.report_generator,
            thresholds=self.thresholds
        )
        
        logger.info("✅ MedAgentBench initialized successfully")
    
    def evaluate(
        self,
        test_data_path: str,
        model_endpoint_url: Optional[str] = None,
        model_endpoint_type: str = "fastapi",
        model_name: Optional[str] = None,
        evaluation_id: Optional[str] = None,
        max_test_cases: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run complete evaluation workflow
        
        Args:
            test_data_path: Path to test JSONL file (local or GCS gs://)
            model_endpoint_url: Model endpoint URL (overrides config)
            model_endpoint_type: Type of endpoint (fastapi, vertex_ai, custom)
            model_name: Name of the model being evaluated
            evaluation_id: Optional evaluation ID
            max_test_cases: Maximum number of test cases to evaluate
            
        Returns:
            Dictionary with evaluation results including:
            - evaluation_status: "PASS" or "FAIL"
            - metrics: Dictionary of all calculated metrics
            - certificate_path: Path to generated PDF certificate
            - report_path: Path to detailed report
            - pass_fail_result: Detailed pass/fail evaluation
        """
        logger.info("=" * 80)
        logger.info("MEDAGENT BENCH - STARTING EVALUATION")
        logger.info("=" * 80)
        
        # Use endpoint from parameter or config
        endpoint_url = model_endpoint_url or self.config.model_endpoint_url
        if not endpoint_url:
            raise ValueError("model_endpoint_url must be provided either as parameter or in config")
        
        # Generate evaluation ID if not provided
        if not evaluation_id:
            evaluation_id = f"medbench_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Run workflow
            result = self.workflow.run(
                test_data_path=test_data_path,
                model_endpoint_url=endpoint_url,
                model_endpoint_type=model_endpoint_type,
                evaluation_id=evaluation_id,
                model_name=model_name,
                max_test_cases=max_test_cases or self.config.max_test_cases
            )
            
            # Extract key results
            evaluation_result = {
                "evaluation_id": result.get("evaluation_id"),
                "model_name": result.get("model_name"),
                "evaluation_status": result.get("evaluation_status", "PENDING"),
                "status": result.get("status"),
                "metrics": result.get("metrics", {}),
                "pass_fail_result": result.get("pass_fail_result", {}),
                "certificate_path": result.get("certificate_path"),
                "report_path": result.get("report_path"),
                "total_test_cases": result.get("total_test_cases", 0),
                "successful_predictions": result.get("successful_predictions", 0),
                "failed_predictions": result.get("failed_predictions", 0),
                "safety_score": result.get("safety_score", 0.0),
                "unsafe_responses": result.get("unsafe_responses", 0),
                "hallucination_score": result.get("hallucination_score", 0.0),
                "timestamp": result.get("evaluation_timestamp")
            }
            
            logger.info("=" * 80)
            logger.info("EVALUATION SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Evaluation ID: {evaluation_result['evaluation_id']}")
            logger.info(f"Model: {evaluation_result['model_name']}")
            logger.info(f"Status: {evaluation_result['evaluation_status']}")
            logger.info(f"Accuracy: {evaluation_result['metrics'].get('accuracy', 0):.3f}")
            logger.info(f"F1 Score: {evaluation_result['metrics'].get('f1_score', 0):.3f}")
            logger.info(f"Safety Score: {evaluation_result['safety_score']:.3f}")
            logger.info(f"Certificate: {evaluation_result['certificate_path']}")
            logger.info("=" * 80)
            
            return evaluation_result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise
    
    def set_thresholds(self, thresholds: EvaluationThresholds):
        """
        Set custom evaluation thresholds
        
        Args:
            thresholds: EvaluationThresholds instance
        """
        self.thresholds = thresholds
        # Recreate workflow with new thresholds
        self.workflow = create_workflow(
            test_loader=self.test_loader,
            model_runner=self.model_runner,
            metrics_calculator=self.metrics_calculator,
            safety_evaluator=self.safety_evaluator,
            report_generator=self.report_generator,
            thresholds=self.thresholds
        )
        logger.info("Custom thresholds applied")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.to_dict()


def create_agent(config: Optional[MedAgentBenchConfig] = None) -> MedAgentBench:
    """
    Factory function to create MedAgentBench instance
    
    Args:
        config: Optional configuration object
        
    Returns:
        MedAgentBench instance
    """
    return MedAgentBench(config=config)

