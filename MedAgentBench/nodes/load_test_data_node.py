"""
Node: Load test data from JSONL file
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def load_test_data_node(
    state: Dict[str, Any],
    test_loader
) -> Dict[str, Any]:
    """
    Load test cases from JSONL file
    
    Args:
        state: Current workflow state
        test_loader: TestLoader tool instance
        
    Returns:
        Updated state with loaded test cases
    """
    logger.info("=" * 60)
    logger.info("NODE: Load Test Data")
    logger.info("=" * 60)
    
    try:
        state["status"] = "loading_test_data"
        state["current_step"] = "load_test_data"
        
        # Get configuration
        test_data_path = state.get("test_data_path")
        if not test_data_path:
            raise ValueError("test_data_path not found in state")
        
        max_cases = state.get("max_test_cases")
        
        # Load test cases
        logger.info(f"Loading test cases from: {test_data_path}")
        test_cases = test_loader.load(
            test_data_path=test_data_path,
            max_cases=max_cases,
            format="jsonl"
        )
        
        # Validate test cases
        valid_cases = []
        for case in test_cases:
            if test_loader.validate_test_case(case):
                valid_cases.append(case)
            else:
                logger.warning(f"Invalid test case skipped: {case.get('case_id', 'unknown')}")
        
        # Extract ground truth
        ground_truth = test_loader.extract_ground_truth(valid_cases)
        
        # Update state
        state["test_cases"] = valid_cases
        state["ground_truth"] = ground_truth
        state["total_test_cases"] = len(valid_cases)
        state["loaded_test_cases"] = len(valid_cases)
        state["status"] = "test_data_loaded"
        
        logger.info(f"✅ Loaded {len(valid_cases)} test cases successfully")
        
        return state
        
    except Exception as e:
        logger.error(f"❌ Failed to load test data: {e}")
        state["status"] = "failed"
        state["error"] = str(e)
        raise

