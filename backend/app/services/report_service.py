import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.domain.interfaces.data_service import IDataService
from app.services.data_service import DataService

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_intelligence_report(self, data: Dict[str, Any]) -> str:
        """
        Generates a comprehensive intelligence report from dashboard/insights data.
        """
        session_id = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"intelligence_report_{session_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"Generating Intelligence PDF report: {filepath}")
        
        try:
            doc = SimpleDocTemplate(filepath, pagesize=LETTER)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            elements.append(Paragraph(f"DeciFlow AI - Strategic Intelligence Report", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Date
            elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            elements.append(Spacer(1, 24))

            # Primary Insights
            elements.append(Paragraph("Strategic Narrative", styles['Heading2']))
            main_insight = data.get("ai_strategic_advice") or data.get("main_insight", "Analysis complete.")
            elements.append(Paragraph(main_insight, styles['Normal']))
            elements.append(Spacer(1, 12))

            # Key Metrics Table
            elements.append(Paragraph("Key Performance Matrix", styles['Heading2']))
            stats = data.get("stats", [])
            metrics_data = [["Metric", "Value", "Trend"]]
            
            for s in stats:
                metrics_data.append([
                    str(s.get("label", "")),
                    str(s.get("value", "")),
                    str(s.get("trend", ""))
                ])
            
            if len(metrics_data) > 1:
                t = Table(metrics_data, colWidths=[150, 150, 150])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1"))
                ]))
                elements.append(t)
                elements.append(Spacer(1, 24))

            # Decisions/Recommendations
            elements.append(Paragraph("Tactical Deployment Matrix", styles['Heading2']))
            decisions = data.get("all_decisions") or []
            for d in decisions:
                elements.append(Paragraph(f"<b>{d.get('action', '')}</b>", styles['Heading3']))
                elements.append(Paragraph(f"Priority: {d.get('priority', '').upper()} | Expected Impact: {d.get('expected_impact', '')}", styles['Normal']))
                elements.append(Paragraph(d.get('reason', ''), styles['Normal']))
                elements.append(Spacer(1, 10))

            doc.build(elements)
            logger.info(f"Intelligence Report generated successfully at {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate Intelligence PDF report: {str(e)}", exc_info=True)
            raise e

    def generate_simulation_report(self, session_id: str, data: Dict[str, Any]) -> str:
        """
        Generates a PDF report for a simulation session.
        Returns the file path of the generated PDF.
        """
        filename = f"simulation_report_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"Generating Simulation PDF report: {filepath}")
        
        try:
            doc = SimpleDocTemplate(filepath, pagesize=LETTER)
            styles = getSampleStyleSheet()
            elements = []

            # Title
            elements.append(Paragraph(f"DeciFlow AI - Strategic Simulation Report", styles['Title']))
            elements.append(Spacer(1, 12))
            
            # Metadata
            elements.append(Paragraph(f"Session ID: {session_id}", styles['Normal']))
            elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            elements.append(Spacer(1, 24))

            # INPUT PARAMETERS SECTION
            elements.append(Paragraph("Scenario Configuration (Inputs)", styles['Heading2']))
            inputs = data.get("inputs", {})
            input_data = [
                ["Parameter", "Configured Value"],
                ["Ad Spend Budget", f"₹{inputs.get('ad_spend', 0):,.2f}"],
                ["Cost per Visit", f"₹{inputs.get('cpc', 0):,.2f}"],
                ["Conversion Rate", f"{inputs.get('conversion_rate', 0)}%"],
                ["Average Sale Value", f"₹{inputs.get('aov', 0):,.2f}"],
                ["Cost to Fulfill", f"₹{inputs.get('unit_cost', 0):,.2f}"],
                ["Target Order Goal", f"{inputs.get('order_goal', 0):,.0f} units"]
            ]
            
            it = Table(input_data, colWidths=[200, 200])
            it.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0"))
            ]))
            elements.append(it)
            elements.append(Spacer(1, 24))

            # Executive Summary
            elements.append(Paragraph("Executive Synthesis", styles['Heading2']))
            narrative = data.get("narrative", "No narrative available.")
            
            # Use regex to strip introductory labels but keep the content
            import re
            clean_narrative = re.sub(r'^(\*\*|)(Executive Summary:|Summary:|Analysis:|Insight:)(\*\*|)\s*', '', narrative, flags=re.IGNORECASE)
            
            elements.append(Paragraph(clean_narrative, styles['Normal']))
            elements.append(Spacer(1, 12))

            # Key Metrics Table
            elements.append(Paragraph("Simulation Outcomes (Results)", styles['Heading2']))
            metrics_data = [
                ["Outcome Metric", "Projected Value"],
                ["Predicted Net Profit", f"₹{data.get('projected_profit', 0):,.2f}"],
                ["Gross Revenue", f"₹{data.get('revenue', 0):,.2f}"],
                ["Expected Conversions", f"{data.get('projected_conversions', 0):,.0f} units"],
                ["Ad Spend Return", str(data.get('roas', "N/A"))],
                ["Acquisition Cost (CAC)", str(data.get('cac', "₹0.00"))],
                ["ROI", str(data.get('roi', "0%"))],
                ["Strategic Risk", str(data.get('risk_level', "Unknown"))]
            ]
            
            t = Table(metrics_data, colWidths=[200, 200])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1"))
            ]))
            elements.append(t)
            elements.append(Spacer(1, 24))

            # Recommendation
            elements.append(Paragraph("Strategic Recommendation", styles['Heading2']))
            rec = data.get("recommendation", "Review parameters and re-run simulation.")
            elements.append(Paragraph(rec, styles['Normal']))

            doc.build(elements)
            logger.info(f"Simulation Report generated successfully at {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate Simulation PDF report: {str(e)}", exc_info=True)
            raise e
