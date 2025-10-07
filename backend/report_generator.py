from fpdf import FPDF
import base64
import tempfile
import os
import logging

class ReportGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def safe_text(self, text, default='N/A'):
        """Ensure text is not empty"""
        if not text or not str(text).strip():
            return default
        return str(text)

    def generate_pdf(self, report_data, charts):
        """Generate PDF report safely"""
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        page_width = pdf.w - 2 * pdf.l_margin  # safe page width

        # Title
        pdf.set_font('Arial', 'B', 20)
        title = self.safe_text(report_data.get('title', 'Report'))[:80]
        pdf.cell(page_width, 10, title, ln=True, align='C')
        pdf.ln(10)

        # Executive Summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(page_width, 10, '1. Executive Summary', ln=True)
        pdf.set_font('Arial', '', 11)
        summary = self.safe_text(report_data.get('executive_summary', 'No executive summary available.'))
        pdf.multi_cell(page_width, 6, summary)
        pdf.ln(5)

        # Key Findings
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(page_width, 10, '2. Key Findings', ln=True)
        pdf.set_font('Arial', '', 11)
        key_findings = report_data.get('key_findings', [])
        if not key_findings:
            key_findings = ['No key findings available.']
        for finding in key_findings:
            pdf.multi_cell(page_width, 6, f'  - {self.safe_text(finding)}')
        pdf.ln(5)

        # Detailed Analysis
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(page_width, 10, '3. Detailed Analysis', ln=True)
        pdf.set_font('Arial', '', 11)
        analysis = self.safe_text(report_data.get('detailed_analysis', 'No detailed analysis available.'))
        pdf.multi_cell(page_width, 6, analysis)
        pdf.ln(5)

        # Charts (if any)
        if charts:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(page_width, 10, '4. Data Visualizations', ln=True)
            pdf.ln(5)
            for chart in charts:
                try:
                    img_data = base64.b64decode(chart.get('image', ''))
                    if not img_data:
                        continue

                    # Save temporarily
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                        tmp.write(img_data)
                        tmp_path = tmp.name

                    # Add to PDF safely
                    pdf.image(tmp_path, x=10, w=page_width)
                    pdf.ln(5)

                    # Clean up
                    os.unlink(tmp_path)
                except Exception as e:
                    self.logger.error(f"Error adding chart to PDF: {e}")

        # Recommendations
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(page_width, 10, '5. Recommendations', ln=True)
        pdf.set_font('Arial', '', 11)
        recommendations = report_data.get('recommendations', [])
        if not recommendations:
            recommendations = ['No recommendations available.']
        for rec in recommendations:
            pdf.multi_cell(page_width, 6, f'  - {self.safe_text(rec)}')
        pdf.ln(5)

        # References / Citations
        citations = report_data.get('citations', [])
        if citations:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(page_width, 10, 'References', ln=True)
            pdf.set_font('Arial', '', 9)
            for citation in citations:
                pdf.multi_cell(page_width, 5, f'  - {self.safe_text(citation)}')

        # Save to temporary file
        output_path = tempfile.mktemp(suffix='.pdf')
        pdf.output(output_path)

        self.logger.info(f"PDF generated: {output_path}")
        return output_path
