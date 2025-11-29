"""
Node: Test model generalization across domains (optional advanced feature)
This node can be used for domain generalization testing if needed.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def generalization_test_node(
    state: Dict[str, Any],
    generalization_evaluator=None
) -> Dict[str, Any]:
    """
    Test model generalization across different domains (optional advanced feature)
    
    Args:
        state: Current workflow state
        generalization_evaluator: Optional generalization evaluator tool
        
    Returns:
        Updated state with generalization test results
    """
    logger.info("=" * 60)
    logger.info("NODE: Generalization Test (Optional)")
    logger.info("=" * 60)
    
    # Check if domain metrics are already calculated
    domain_metrics = state.get("domain_metrics", {})
    
    if domain_metrics:
        logger.info(f"Domain-specific metrics already calculated for {len(domain_metrics)} domains")
        state["generalization_test"] = {
            "status": "completed",
            "domains_tested": list(domain_metrics.keys()),
            "metrics": domain_metrics
        }
    else:
        logger.info("Generalization test skipped - no domain information available")
        state["generalization_test"] = {
            "status": "skipped",
            "note": "No domain-specific metrics available"
        }
    
    return state

