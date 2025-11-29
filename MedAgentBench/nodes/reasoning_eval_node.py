"""
Node: Evaluate reasoning quality (optional advanced feature)
This node can be used for advanced reasoning evaluation if needed.
Currently, basic reasoning is evaluated through accuracy metrics.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def reasoning_eval_node(
    state: Dict[str, Any],
    reasoning_evaluator=None
) -> Dict[str, Any]:
    """
    Evaluate reasoning quality of predictions (optional advanced feature)
    
    Args:
        state: Current workflow state
        reasoning_evaluator: Optional reasoning evaluator tool
        
    Returns:
        Updated state with reasoning evaluation results
    """
    logger.info("=" * 60)
    logger.info("NODE: Reasoning Evaluation (Optional)")
    logger.info("=" * 60)
    
    # This is an optional advanced feature
    # For now, we'll skip it and use accuracy as a proxy for reasoning
    logger.info("Reasoning evaluation skipped - using accuracy metrics as proxy")
    
    state["reasoning_evaluation"] = {
        "status": "skipped",
        "note": "Reasoning evaluation is optional. Accuracy metrics serve as basic reasoning proxy."
    }
    
    return state

