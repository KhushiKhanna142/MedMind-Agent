"""
Node: Calculate evaluation metrics and scores
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def calculate_scores_node(
    state: Dict[str, Any],
    metrics_calculator
) -> Dict[str, Any]:
    """
    Calculate accuracy, precision, recall, F1 score from predictions
    
    Args:
        state: Current workflow state
        metrics_calculator: MetricsCalculator tool instance
        
    Returns:
        Updated state with calculated metrics
    """
    logger.info("=" * 60)
    logger.info("NODE: Calculate Scores")
    logger.info("=" * 60)
    
    try:
        state["status"] = "calculating_scores"
        state["current_step"] = "calculate_scores"
        
        # Get predictions and ground truth
        predictions = state.get("predictions", [])
        ground_truth = state.get("ground_truth", [])
        
        if not predictions:
            raise ValueError("No predictions found in state")
        if not ground_truth:
            raise ValueError("No ground truth found in state")
        
        logger.info(f"Calculating metrics for {len(predictions)} predictions")
        
        # Determine task type
        task_type = state.get("task_type", "classification")
        
        # Calculate metrics
        metrics = metrics_calculator.calculate(
            predictions=predictions,
            ground_truth=ground_truth,
            task_type=task_type
        )
        
        # Calculate per-domain metrics if domain information available
        domain_metrics = {}
        if any(p.get("metadata", {}).get("domain") for p in predictions):
            domain_metrics = metrics_calculator.calculate_per_domain(
                predictions=predictions,
                ground_truth=ground_truth,
                domain_key="domain"
            )
        
        # Update state with metrics
        state["metrics"] = metrics
        
        # Update individual metric fields
        state["accuracy"] = metrics.get("accuracy", 0.0)
        state["precision"] = metrics.get("precision", 0.0)
        state["recall"] = metrics.get("recall", 0.0)
        state["f1_score"] = metrics.get("f1_score", 0.0)
        
        if domain_metrics:
            state["domain_metrics"] = domain_metrics
        
        state["status"] = "scores_calculated"
        
        logger.info(f"✅ Metrics calculated")
        logger.info(f"   Accuracy: {metrics.get('accuracy', 0):.3f}")
        logger.info(f"   Precision: {metrics.get('precision', 0):.3f}")
        logger.info(f"   Recall: {metrics.get('recall', 0):.3f}")
        logger.info(f"   F1 Score: {metrics.get('f1_score', 0):.3f}")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Failed to calculate scores: {e}")
        state["status"] = "failed"
        state["error"] = str(e)
        raise
