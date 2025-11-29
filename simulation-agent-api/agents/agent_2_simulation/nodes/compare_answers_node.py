"""
Node: Compare model answers with benchmark answers
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def compare_answers_node(
    state: Dict[str, Any],
    answer_comparator
) -> Dict[str, Any]:
    """
    Compare model-generated answers with benchmark answers
    
    Args:
        state: Current workflow state
        answer_comparator: AnswerComparator tool instance
        
    Returns:
        Updated state with comparison results
    """
    logger.info("=" * 60)
    logger.info("NODE: Compare Answers")
    logger.info("=" * 60)
    
    try:
        state["status"] = "comparing_answers"
        
        # Get answers
        model_answers = state.get("model_answers", [])
        benchmark_answers = state.get("benchmark_answers", [])
        questions = state.get("simulation_questions", [])
        
        if len(model_answers) != len(benchmark_answers):
            raise ValueError(
                f"Answer count mismatch: {len(model_answers)} model answers vs "
                f"{len(benchmark_answers)} benchmark answers"
            )
        
        logger.info(f"Comparing {len(model_answers)} answer pairs")
        
        # Compare answers
        comparison_results = answer_comparator.compare(
            model_answers=model_answers,
            benchmark_answers=benchmark_answers,
            questions=questions
        )
        
        # Extract indices
        correct_indices = comparison_results.get("correct_indices", [])
        incorrect_indices = comparison_results.get("incorrect_indices", [])
        
        # Update state
        state["comparison_results"] = comparison_results
        state["correct_indices"] = correct_indices
        state["incorrect_indices"] = incorrect_indices
        state["comparison_completed"] = True
        state["status"] = "calculating_metrics"
        
        logger.info(f"✅ Comparison completed")
        logger.info(f"✔️  Correct answers: {len(correct_indices)}")
        logger.info(f"❌ Incorrect answers: {len(incorrect_indices)}")
        
    except Exception as e:
        logger.error(f"❌ Answer comparison failed: {str(e)}")
        state["status"] = "failed"
        state["errors"].append(f"Comparison error: {str(e)}")
        raise
    
    return state