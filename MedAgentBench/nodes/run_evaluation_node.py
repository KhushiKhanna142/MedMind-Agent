"""
Node: Run model evaluation on test cases
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def run_evaluation_node(
    state: Dict[str, Any],
    model_runner
) -> Dict[str, Any]:
    """
    Run inference on all test cases using model endpoint
    
    Args:
        state: Current workflow state
        model_runner: ModelRunner tool instance
        
    Returns:
        Updated state with predictions
    """
    logger.info("=" * 60)
    logger.info("NODE: Run Evaluation")
    logger.info("=" * 60)
    
    try:
        state["status"] = "running_evaluation"
        state["current_step"] = "run_evaluation"
        
        # Get test cases
        test_cases = state.get("test_cases", [])
        if not test_cases:
            raise ValueError("No test cases found in state")
        
        logger.info(f"Running evaluation on {len(test_cases)} test cases")
        
        # Get parallel setting
        parallel = state.get("parallel_requests", True)
        
        # Run inference
        predictions = model_runner.run_inference(
            test_cases=test_cases,
            parallel=parallel
        )
        
        # Separate successful and failed predictions
        successful_preds = [p for p in predictions if p.get("success", True)]
        failed_preds = [p for p in predictions if not p.get("success", True)]
        
        # Update state
        state["predictions"] = predictions
        state["successful_predictions"] = len(successful_preds)
        state["failed_predictions"] = len(failed_preds)
        state["failed_cases"] = [p.get("case_id") for p in failed_preds]
        
        if failed_preds:
            state["error_details"] = [
                {
                    "case_id": p.get("case_id"),
                    "error": p.get("error")
                }
                for p in failed_preds
            ]
        
        state["status"] = "evaluation_completed"
        
        logger.info(f"✅ Evaluation completed")
        logger.info(f"   Successful: {len(successful_preds)}")
        logger.info(f"   Failed: {len(failed_preds)}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Failed to run evaluation: {e}")
        state["status"] = "failed"
        state["error"] = str(e)
        raise

