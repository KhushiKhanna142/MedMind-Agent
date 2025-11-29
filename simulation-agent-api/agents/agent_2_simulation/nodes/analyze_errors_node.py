"""
Node: Analyze errors and provide improvement suggestions
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def analyze_errors_node(
    state: Dict[str, Any],
    error_analyzer
) -> Dict[str, Any]:
    """
    Analyze incorrect answers and provide improvement suggestions
    
    Args:
        state: Current workflow state
        error_analyzer: ErrorAnalyzer tool instance
        
    Returns:
        Updated state with error analysis and suggestions
    """
    logger.info("=" * 60)
    logger.info("NODE: Analyze Errors")
    logger.info("=" * 60)
    
    try:
        state["status"] = "analyzing_errors"
        
        # Get data for analysis
        questions = state.get("simulation_questions", [])
        model_answers = state.get("model_answers", [])
        benchmark_answers = state.get("benchmark_answers", [])
        incorrect_indices = state.get("incorrect_indices", [])
        
        if not incorrect_indices:
            logger.info("No errors to analyze")
            state["error_analysis"] = {"total_errors": 0}
            state["error_types"] = {}
            state["error_examples"] = []
            state["improvement_suggestions"] = []
            state["status"] = "completed"
            return state
        
        logger.info(f"Analyzing {len(incorrect_indices)} incorrect answers")
        
        # Perform error analysis
        error_analysis = error_analyzer.analyze(
            questions=questions,
            model_answers=model_answers,
            benchmark_answers=benchmark_answers,
            incorrect_indices=incorrect_indices
        )
        
        # Extract components
        error_types = error_analysis.get("error_types", {})
        error_examples = error_analysis.get("error_examples", [])
        improvement_suggestions = error_analysis.get("suggestions", [])
        
        # Update state
        state["error_analysis"] = error_analysis
        state["error_types"] = error_types
        state["error_examples"] = error_examples
        state["improvement_suggestions"] = improvement_suggestions
        state["status"] = "completed"
        
        # Log analysis
        logger.info("=" * 60)
        logger.info("🔍 ERROR ANALYSIS")
        logger.info("=" * 60)
        logger.info(f"Total Errors: {len(incorrect_indices)}")
        logger.info("")
        logger.info("Error Types:")
        for error_type, count in error_types.items():
            logger.info(f"  {error_type}: {count}")
        logger.info("")
        logger.info("Improvement Suggestions:")
        for i, suggestion in enumerate(improvement_suggestions, 1):
            logger.info(f"  {i}. {suggestion}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Error analysis failed: {str(e)}")
        state["status"] = "failed"
        state["errors"].append(f"Error analysis error: {str(e)}")
        raise
    
    return state