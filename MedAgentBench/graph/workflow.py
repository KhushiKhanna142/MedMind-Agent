"""
Workflow graph for MedAgentBench evaluation process using LangGraph
"""

import logging
from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END

from .state import EvaluationState, create_initial_state
from nodes.load_test_data_node import load_test_data_node
from nodes.run_evaluation_node import run_evaluation_node
from nodes.calculate_scores_node import calculate_scores_node
from nodes.safety_eval_node import safety_eval_node
from nodes.generate_report_node import generate_report_node

logger = logging.getLogger(__name__)


def should_continue(state: Dict[str, Any]) -> str:
    """
    Conditional edge function to determine next step
    
    Args:
        state: Current workflow state
        
    Returns:
        Next node name or END
    """
    status = state.get("status", "")
    
    # Check for failure
    if status == "failed":
        return END
    
    # Routing based on current step
    current_step = state.get("current_step", "")
    
    if current_step == "load_test_data":
        return "run_evaluation"
    elif current_step == "run_evaluation":
        return "calculate_scores"
    elif current_step == "calculate_scores":
        return "safety_eval"
    elif current_step == "safety_eval":
        return "generate_report"
    elif current_step == "generate_report" or status == "completed":
        return END
    
    return END


class MedAgentBenchWorkflow:
    """
    LangGraph-based workflow orchestrator for MedAgentBench evaluation
    """
    
    def __init__(
        self,
        test_loader,
        model_runner,
        metrics_calculator,
        safety_evaluator,
        report_generator,
        thresholds
    ):
        """
        Initialize workflow with all required tools
        
        Args:
            test_loader: TestLoader instance
            model_runner: ModelRunner instance
            metrics_calculator: MetricsCalculator instance
            safety_evaluator: SafetyEvaluator instance
            report_generator: ReportGenerator instance
            thresholds: EvaluationThresholds instance
        """
        self.test_loader = test_loader
        self.model_runner = model_runner
        self.metrics_calculator = metrics_calculator
        self.safety_evaluator = safety_evaluator
        self.report_generator = report_generator
        self.thresholds = thresholds
        
        # Build the LangGraph StateGraph
        self.graph = self._build_graph()
        
        logger.info("✅ MedAgentBenchWorkflow initialized with LangGraph StateGraph")
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph StateGraph for evaluation workflow
        
        Returns:
            Compiled StateGraph
        """
        # Create StateGraph
        workflow = StateGraph(dict)
        
        # Add nodes with bound tools
        workflow.add_node(
            "load_test_data",
            lambda state: load_test_data_node(state, self.test_loader)
        )
        workflow.add_node(
            "run_evaluation",
            lambda state: run_evaluation_node(state, self.model_runner)
        )
        workflow.add_node(
            "calculate_scores",
            lambda state: calculate_scores_node(state, self.metrics_calculator)
        )
        workflow.add_node(
            "safety_eval",
            lambda state: safety_eval_node(state, self.safety_evaluator)
        )
        workflow.add_node(
            "generate_report",
            lambda state: generate_report_node(state, self.report_generator, self.thresholds)
        )
        
        # Set entry point
        workflow.set_entry_point("load_test_data")
        
        # Add edges (linear workflow)
        workflow.add_edge("load_test_data", "run_evaluation")
        workflow.add_edge("run_evaluation", "calculate_scores")
        workflow.add_edge("calculate_scores", "safety_eval")
        workflow.add_edge("safety_eval", "generate_report")
        workflow.add_edge("generate_report", END)
        
        # Compile the graph
        return workflow.compile()
    
    def run(
        self,
        test_data_path: str,
        model_endpoint_url: str,
        model_endpoint_type: str = "fastapi",
        evaluation_id: Optional[str] = None,
        model_name: Optional[str] = None,
        max_test_cases: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run the complete evaluation workflow using LangGraph
        
        Args:
            test_data_path: Path to test JSONL file
            model_endpoint_url: Model endpoint URL
            model_endpoint_type: Type of endpoint (fastapi, vertex_ai, etc.)
            evaluation_id: Optional evaluation ID
            model_name: Optional model name
            max_test_cases: Maximum number of test cases to evaluate
            
        Returns:
            Final evaluation state as dictionary
        """
        logger.info("=" * 60)
        logger.info("STARTING MEDAGENT BENCH EVALUATION (LangGraph)")
        logger.info("=" * 60)
        
        # Create initial state
        initial_state = create_initial_state(
            test_data_path=test_data_path,
            model_endpoint_url=model_endpoint_url,
            model_endpoint_type=model_endpoint_type,
            evaluation_id=evaluation_id,
            model_name=model_name
        )
        
        if max_test_cases:
            initial_state.max_test_cases = max_test_cases
        
        # Convert to dict for workflow
        state_dict = initial_state.to_dict()
        
        try:
            # Run the LangGraph workflow
            logger.info("🚀 Executing LangGraph StateGraph workflow...")
            final_state = self.graph.invoke(state_dict)
            
            logger.info("=" * 60)
            logger.info("EVALUATION COMPLETED")
            logger.info("=" * 60)
            logger.info(f"Status: {final_state.get('status')}")
            logger.info(f"Evaluation Status: {final_state.get('evaluation_status')}")
            
            if final_state.get('certificate_path'):
                logger.info(f"Certificate: {final_state['certificate_path']}")
            if final_state.get('report_path'):
                logger.info(f"Report: {final_state['report_path']}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            state_dict["status"] = "failed"
            state_dict["error"] = str(e)
            raise


def create_workflow(
    test_loader,
    model_runner,
    metrics_calculator,
    safety_evaluator,
    report_generator,
    thresholds
) -> MedAgentBenchWorkflow:
    """
    Factory function to create workflow instance
    
    Args:
        test_loader: TestLoader instance
        model_runner: ModelRunner instance
        metrics_calculator: MetricsCalculator instance
        safety_evaluator: SafetyEvaluator instance
        report_generator: ReportGenerator instance
        thresholds: EvaluationThresholds instance
        
    Returns:
        MedAgentBenchWorkflow instance
    """
    return MedAgentBenchWorkflow(
        test_loader=test_loader,
        model_runner=model_runner,
        metrics_calculator=metrics_calculator,
        safety_evaluator=safety_evaluator,
        report_generator=report_generator,
        thresholds=thresholds
    )

