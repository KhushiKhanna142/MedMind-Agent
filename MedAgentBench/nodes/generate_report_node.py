"""
Node: Generate evaluation certificate and report
"""

from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_report_node(
    state: Dict[str, Any],
    report_generator,
    thresholds
) -> Dict[str, Any]:
    """
    Generate evaluation certificate (PDF) and detailed report
    
    Args:
        state: Current workflow state
        report_generator: ReportGenerator tool instance
        thresholds: EvaluationThresholds instance
        
    Returns:
        Updated state with report paths
    """
    logger.info("=" * 60)
    logger.info("NODE: Generate Report")
    logger.info("=" * 60)
    
    try:
        state["status"] = "generating_report"
        state["current_step"] = "generate_report"
        
        # Prepare metrics for pass/fail evaluation
        metrics = state.get("metrics", {})
        domain = state.get("domain", "general")
        
        # Evaluate pass/fail
        logger.info("Evaluating PASS/FAIL criteria")
        pass_fail_result = thresholds.evaluate_pass_fail(
            metrics=metrics,
            domain=domain
        )
        
        state["pass_fail_result"] = pass_fail_result
        state["evaluation_status"] = pass_fail_result.get("status", "PENDING")
        
        # Prepare state for certificate generation
        eval_state_dict = {
            "evaluation_id": state.get("evaluation_id"),
            "model_name": state.get("model_name", "Unknown Model"),
            "evaluation_timestamp": state.get("evaluation_timestamp", datetime.now().isoformat()),
            "metrics": metrics,
            "accuracy": state.get("accuracy", 0.0),
            "precision": state.get("precision", 0.0),
            "recall": state.get("recall", 0.0),
            "f1_score": state.get("f1_score", 0.0),
            "safety_score": state.get("safety_score", 1.0),
            "hallucination_score": state.get("hallucination_score", 0.0),
            "unsafe_responses": state.get("unsafe_responses", 0),
            "total_test_cases": state.get("total_test_cases", 0),
            "pass_fail_result": pass_fail_result,
            "evaluation_status": state["evaluation_status"]
        }
        
        # Generate certificate
        logger.info("Generating evaluation certificate (PDF)")
        certificate_path = report_generator.generate_certificate(eval_state_dict)
        state["certificate_path"] = certificate_path
        state["certificate_generated"] = True
        
        # Generate detailed report
        logger.info("Generating detailed evaluation report")
        report_path = report_generator.generate_detailed_report(eval_state_dict)
        state["report_path"] = report_path
        
        state["status"] = "completed"
        state["current_step"] = "completed"
        
        logger.info(f"✅ Report generation completed")
        logger.info(f"   Certificate: {certificate_path}")
        logger.info(f"   Report: {report_path}")
        logger.info(f"   Evaluation Status: {state['evaluation_status']}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Failed to generate report: {e}")
        state["status"] = "failed"
        state["error"] = str(e)
        raise

