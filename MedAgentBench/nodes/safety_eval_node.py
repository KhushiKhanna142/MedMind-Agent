"""
Node: Evaluate safety and detect hallucinations
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def safety_eval_node(
    state: Dict[str, Any],
    safety_evaluator
) -> Dict[str, Any]:
    """
    Evaluate safety and hallucination scores
    
    Args:
        state: Current workflow state
        safety_evaluator: SafetyEvaluator tool instance
        
    Returns:
        Updated state with safety evaluation results
    """
    logger.info("=" * 60)
    logger.info("NODE: Safety Evaluation")
    logger.info("=" * 60)
    
    try:
        state["status"] = "evaluating_safety"
        state["current_step"] = "safety_evaluation"
        
        # Get predictions and ground truth
        predictions = state.get("predictions", [])
        ground_truth = state.get("ground_truth", [])
        
        if not predictions:
            raise ValueError("No predictions found in state")
        
        logger.info(f"Evaluating safety for {len(predictions)} predictions")
        
        # Evaluate safety
        safety_results = safety_evaluator.evaluate(
            predictions=predictions,
            ground_truth=ground_truth if ground_truth else None
        )
        
        # Update state with safety metrics
        state["safety_evaluation"] = safety_results
        state["safety_score"] = safety_results.get("safety_score", 1.0)
        state["unsafe_responses"] = safety_results.get("unsafe_responses", 0)
        state["safety_issues"] = safety_results.get("unsafe_response_details", [])
        state["hallucination_score"] = safety_results.get("hallucination_score", 0.0)
        
        # Update metrics dictionary
        if "metrics" not in state:
            state["metrics"] = {}
        state["metrics"]["safety_score"] = safety_results.get("safety_score", 1.0)
        state["metrics"]["hallucination_score"] = safety_results.get("hallucination_score", 0.0)
        state["metrics"]["unsafe_responses"] = safety_results.get("unsafe_responses", 0)
        
        state["status"] = "safety_evaluation_completed"
        
        logger.info(f"✅ Safety evaluation completed")
        logger.info(f"   Safety Score: {state['safety_score']:.3f}")
        logger.info(f"   Unsafe Responses: {state['unsafe_responses']}")
        logger.info(f"   Hallucination Score: {state['hallucination_score']:.3f}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Failed to evaluate safety: {e}")
        state["status"] = "failed"
        state["error"] = str(e)
        raise

