"""
Tool: Generate evaluation certificate (PDF) and report
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import json

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("reportlab not available. PDF generation will use basic method.")

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generate evaluation reports and certificates in PDF format
    """
    
    def __init__(self, config=None):
        """
        Initialize Report Generator
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.output_dir = Path(
            config.certificate_output_path if config
            else "reports/certificates/"
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"ReportGenerator initialized with output: {self.output_dir}")
    
    def generate_certificate(
        self,
        evaluation_state: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate evaluation certificate PDF
        
        Args:
            evaluation_state: Evaluation state dictionary with metrics and results
            output_path: Optional custom output path
            
        Returns:
            Path to generated certificate file
        """
        logger.info("Generating evaluation certificate")
        
        if output_path:
            cert_path = Path(output_path)
        else:
            eval_id = evaluation_state.get("evaluation_id", f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            cert_path = self.output_dir / f"certificate_{eval_id}.pdf"
        
        cert_path.parent.mkdir(parents=True, exist_ok=True)
        
        if REPORTLAB_AVAILABLE:
            self._generate_certificate_pdf(evaluation_state, str(cert_path))
        else:
            self._generate_certificate_basic(evaluation_state, str(cert_path))
        
        logger.info(f"✅ Certificate generated: {cert_path}")
        return str(cert_path)
    
    def _generate_certificate_pdf(
        self,
        evaluation_state: Dict[str, Any],
        output_path: str
    ):
        """Generate certificate using ReportLab"""
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a237e'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        story.append(Paragraph("Medical AI Model Evaluation Certificate", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Model Information
        model_name = evaluation_state.get("model_name", "Unknown Model")
        eval_id = evaluation_state.get("evaluation_id", "N/A")
        eval_date = evaluation_state.get("evaluation_timestamp", datetime.now().isoformat())
        
        info_data = [
            ["Model Name:", model_name],
            ["Evaluation ID:", eval_id],
            ["Evaluation Date:", eval_date.split('T')[0] if 'T' in eval_date else eval_date],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Evaluation Results
        metrics = evaluation_state.get("metrics", {})
        pass_fail = evaluation_state.get("pass_fail_result", {})
        status = pass_fail.get("status", "PENDING")
        overall_score = pass_fail.get("overall_score", 0.0)
        
        # Status header
        status_color = colors.HexColor('#4caf50') if status == "PASS" else colors.HexColor('#f44336')
        status_style = ParagraphStyle(
            'Status',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=status_color,
            alignment=1
        )
        story.append(Paragraph(f"Evaluation Status: {status}", status_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Metrics table
        metrics_data = [
            ["Metric", "Score", "Threshold", "Status"]
        ]
        
        thresholds = {
            "accuracy": 0.80,
            "precision": 0.75,
            "recall": 0.75,
            "f1_score": 0.75,
            "safety_score": 0.95
        }
        
        metric_names = {
            "accuracy": "Accuracy",
            "precision": "Precision",
            "recall": "Recall",
            "f1_score": "F1 Score",
            "safety_score": "Safety Score",
            "hallucination_score": "Hallucination Score"
        }
        
        for metric_key, metric_name in metric_names.items():
            if metric_key in metrics:
                value = metrics[metric_key]
                threshold = thresholds.get(metric_key, 0.0)
                passed = value >= threshold if metric_key != "hallucination_score" else value <= 0.10
                status_symbol = "✓" if passed else "✗"
                
                # Format values
                if metric_key == "hallucination_score":
                    value_str = f"{value:.3f} (lower is better)"
                    threshold_str = "≤ 0.10"
                else:
                    value_str = f"{value:.3f}"
                    threshold_str = f"≥ {threshold:.2f}"
                
                metrics_data.append([
                    metric_name,
                    value_str,
                    threshold_str,
                    status_symbol
                ])
        
        # Overall score
        metrics_data.append([
            "Overall Score",
            f"{overall_score:.3f}",
            "≥ 0.75",
            "✓" if overall_score >= 0.75 else "✗"
        ])
        
        metrics_table = Table(metrics_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(metrics_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Summary
        summary_style = ParagraphStyle(
            'Summary',
            parent=styles['BodyText'],
            fontSize=11,
            leading=14
        )
        
        total_cases = evaluation_state.get("total_test_cases", 0)
        unsafe_count = evaluation_state.get("unsafe_responses", 0)
        
        summary_text = f"""
        <b>Evaluation Summary:</b><br/>
        • Total test cases evaluated: {total_cases}<br/>
        • Unsafe responses detected: {unsafe_count}<br/>
        • Overall evaluation: <b>{status}</b><br/>
        • Overall score: {overall_score:.1%}<br/>
        """
        
        if pass_fail.get("failures"):
            summary_text += "<br/><b>Failures:</b><br/>"
            for failure in pass_fail.get("failures", [])[:5]:  # Show max 5
                summary_text += f"• {failure}<br/>"
        
        story.append(Paragraph(summary_text, summary_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph(
            "This certificate is generated by MedAgentBench Evaluation System",
            footer_style
        ))
        
        doc.build(story)
    
    def _generate_certificate_basic(
        self,
        evaluation_state: Dict[str, Any],
        output_path: str
    ):
        """Generate basic certificate if ReportLab not available"""
        # Create a simple text/JSON certificate
        cert_data = {
            "certificate_type": "Medical AI Model Evaluation",
            "evaluation_state": evaluation_state,
            "generated_at": datetime.now().isoformat()
        }
        
        # Try to save as JSON
        json_path = output_path.replace('.pdf', '.json')
        with open(json_path, 'w') as f:
            json.dump(cert_data, f, indent=2)
        
        logger.warning(f"ReportLab not available. Generated JSON certificate: {json_path}")
        logger.warning("Install reportlab for PDF generation: pip install reportlab")
    
    def generate_detailed_report(
        self,
        evaluation_state: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate detailed evaluation report (JSON)
        
        Args:
            evaluation_state: Evaluation state dictionary
            output_path: Optional custom output path
            
        Returns:
            Path to generated report file
        """
        logger.info("Generating detailed evaluation report")
        
        if output_path:
            report_path = Path(output_path)
        else:
            eval_id = evaluation_state.get("evaluation_id", f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            report_dir = Path(
                self.config.report_output_path if self.config
                else "reports/evaluations/"
            )
            report_dir.mkdir(parents=True, exist_ok=True)
            report_path = report_dir / f"report_{eval_id}.json"
        
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create comprehensive report
        report = {
            "report_type": "MedAgentBench Detailed Evaluation Report",
            "generated_at": datetime.now().isoformat(),
            "evaluation_state": evaluation_state,
            "summary": {
                "model_name": evaluation_state.get("model_name"),
                "evaluation_id": evaluation_state.get("evaluation_id"),
                "status": evaluation_state.get("evaluation_status"),
                "overall_score": evaluation_state.get("pass_fail_result", {}).get("overall_score"),
                "total_cases": evaluation_state.get("total_test_cases", 0)
            }
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"✅ Report generated: {report_path}")
        return str(report_path)

