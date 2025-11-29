"""
Conditional logic for workflow transitions
"""

from typing import Dict, Any


def should_continue(state: Dict[str, Any]) -> str:
    """
    Determine next workflow step based on state
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name
    """
    status = state.get("status", "")
    error = state.get("error")
    
    # If there's an error, stop
    if error:
        return "END"
    
    # Default linear flow (handled by workflow edges)
    return "continue"


def check_evaluation_complete(state: Dict[str, Any]) -> bool:
    """
    Check if evaluation is complete
    
    Args:
        state: Current workflow state
        
    Returns:
        True if complete, False otherwise
    """
    status = state.get("status")
    return status == "completed" or status == "failed"

