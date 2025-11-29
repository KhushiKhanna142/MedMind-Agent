"""
Tool: Calculate evaluation metrics (accuracy, precision, recall, F1, etc.)
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """
    Calculate evaluation metrics for model predictions
    """
    
    def __init__(self, config=None):
        """
        Initialize Metrics Calculator
        
        Args:
            config: Configuration object
        """
        self.config = config
        logger.info("MetricsCalculator initialized")
    
    def calculate(
        self,
        predictions: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]],
        task_type: str = "classification"
    ) -> Dict[str, float]:
        """
        Calculate comprehensive evaluation metrics
        
        Args:
            predictions: List of prediction dictionaries with 'case_id' and 'prediction'
            ground_truth: List of ground truth dictionaries with 'case_id' and expected value
            task_type: Type of task (classification, regression, generation)
            
        Returns:
            Dictionary of calculated metrics
        """
        logger.info(f"Calculating metrics for {len(predictions)} predictions")
        
        if len(predictions) != len(ground_truth):
            raise ValueError(
                f"Prediction count ({len(predictions)}) doesn't match "
                f"ground truth count ({len(ground_truth)})"
            )
        
        # Create mapping by case_id
        pred_dict = {p.get("case_id"): p for p in predictions}
        gt_dict = {g.get("case_id"): g for g in ground_truth}
        
        # Align predictions and ground truth
        aligned_preds = []
        aligned_truths = []
        
        for case_id in pred_dict.keys():
            if case_id in gt_dict:
                aligned_preds.append(pred_dict[case_id])
                aligned_truths.append(gt_dict[case_id])
        
        if task_type == "classification":
            metrics = self._calculate_classification_metrics(aligned_preds, aligned_truths)
        elif task_type == "generation":
            metrics = self._calculate_generation_metrics(aligned_preds, aligned_truths)
        else:
            metrics = self._calculate_general_metrics(aligned_preds, aligned_truths)
        
        logger.info(f"✅ Metrics calculated successfully")
        return metrics
    
    def _calculate_classification_metrics(
        self,
        predictions: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate metrics for classification tasks"""
        
        # Extract labels
        y_pred = []
        y_true = []
        
        for pred, gt in zip(predictions, ground_truth):
            pred_label = self._extract_label(pred.get("prediction"))
            true_label = self._extract_label(gt.get("expected_label") or gt.get("expected_output"))
            
            if pred_label is not None and true_label is not None:
                y_pred.append(pred_label)
                y_true.append(true_label)
        
        if not y_pred or not y_true:
            logger.warning("No valid labels found for metric calculation")
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0
            }
        
        # Calculate metrics
        try:
            accuracy = float(accuracy_score(y_true, y_pred))
            
            # Use micro averaging for multi-class
            precision = float(precision_score(y_true, y_pred, average='weighted', zero_division=0))
            recall = float(recall_score(y_true, y_pred, average='weighted', zero_division=0))
            f1 = float(f1_score(y_true, y_pred, average='weighted', zero_division=0))
            
            metrics = {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            }
            
            # Add per-class metrics if binary or small number of classes
            unique_labels = list(set(y_true + y_pred))
            if len(unique_labels) <= 10:
                report = classification_report(
                    y_true, y_pred, output_dict=True, zero_division=0
                )
                metrics["classification_report"] = report
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating classification metrics: {e}")
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0
            }
    
    def _calculate_generation_metrics(
        self,
        predictions: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate metrics for text generation tasks"""
        
        from difflib import SequenceMatcher
        
        similarities = []
        
        for pred, gt in zip(predictions, ground_truth):
            pred_text = str(pred.get("prediction", "")).lower().strip()
            true_text = str(gt.get("expected_output", "")).lower().strip()
            
            if pred_text and true_text:
                similarity = SequenceMatcher(None, pred_text, true_text).ratio()
                similarities.append(similarity)
        
        if similarities:
            avg_similarity = float(np.mean(similarities))
            
            # Use similarity as a proxy for accuracy in generation tasks
            return {
                "accuracy": avg_similarity,
                "precision": avg_similarity,  # Approximate
                "recall": avg_similarity,  # Approximate
                "f1_score": avg_similarity,  # Approximate
                "text_similarity": avg_similarity
            }
        
        return {
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "text_similarity": 0.0
        }
    
    def _calculate_general_metrics(
        self,
        predictions: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate general metrics for any task type"""
        
        correct = 0
        total = len(predictions)
        
        for pred, gt in zip(predictions, ground_truth):
            pred_value = pred.get("prediction")
            true_value = gt.get("expected_output") or gt.get("expected_label")
            
            if self._values_match(pred_value, true_value):
                correct += 1
        
        accuracy = correct / total if total > 0 else 0.0
        
        return {
            "accuracy": accuracy,
            "precision": accuracy,  # Approximate for general case
            "recall": accuracy,  # Approximate for general case
            "f1_score": accuracy  # Approximate for general case
        }
    
    def _extract_label(self, value: Any) -> Optional[str]:
        """Extract label from various formats"""
        if value is None:
            return None
        
        if isinstance(value, str):
            # Try to extract label from format like "A) Option", "B) Answer"
            if ") " in value:
                return value.split(") ", 1)[0].strip()
            return value.strip()
        
        if isinstance(value, (int, float)):
            return str(value)
        
        if isinstance(value, dict):
            return value.get("label") or value.get("class") or str(value)
        
        return str(value)
    
    def _values_match(self, pred: Any, truth: Any) -> bool:
        """Check if prediction matches ground truth"""
        if pred is None or truth is None:
            return False
        
        # Normalize strings
        pred_str = str(pred).lower().strip()
        truth_str = str(truth).lower().strip()
        
        # Exact match
        if pred_str == truth_str:
            return True
        
        # Check if prediction contains ground truth or vice versa
        if truth_str in pred_str or pred_str in truth_str:
            return True
        
        # For numeric values, allow small tolerance
        try:
            pred_num = float(pred_str)
            truth_num = float(truth_str)
            return abs(pred_num - truth_num) < 0.001
        except ValueError:
            pass
        
        return False
    
    def calculate_per_domain(
        self,
        predictions: List[Dict[str, Any]],
        ground_truth: List[Dict[str, Any]],
        domain_key: str = "domain"
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate metrics per domain
        
        Args:
            predictions: List of predictions
            ground_truth: List of ground truth
            domain_key: Key to extract domain from metadata
            
        Returns:
            Dictionary mapping domain to metrics
        """
        # Group by domain
        domain_preds = {}
        domain_truths = {}
        
        for pred, gt in zip(predictions, ground_truth):
            domain = (
                pred.get("metadata", {}).get(domain_key) or
                gt.get("metadata", {}).get(domain_key) or
                "unknown"
            )
            
            if domain not in domain_preds:
                domain_preds[domain] = []
                domain_truths[domain] = []
            
            domain_preds[domain].append(pred)
            domain_truths[domain].append(gt)
        
        # Calculate metrics per domain
        domain_metrics = {}
        for domain in domain_preds.keys():
            domain_metrics[domain] = self.calculate(
                domain_preds[domain],
                domain_truths[domain]
            )
        
        return domain_metrics

