import logging
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import UUID

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, 
    Paragraph, 
    Spacer, 
    PageBreak, 
    Image
)

# Setup logger
logger = logging.getLogger(__name__)

class PDFGenerator:
    """
    Converts the text-based 'Unified Brain' into a physical PDF document.
    
    Features:
    1. Branding: Generates a distinct 'AetherDocs' cover page.
    2. Dynamic Parsing: Converts LLM Markdown (#, ##, *) into ReportLab styles.
    3. Typography: Uses a clean, academic layout.
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Define custom paragraph styles for the Common Book."""
        # Title Style (Cover Page)
        self.styles.add(ParagraphStyle(
            name='AetherTitle',
            parent=self.styles['Title'],
            fontSize=32,
            leading=40,
            alignment=TA_CENTER,
            spaceAfter=50,
            textColor=colors.HexColor('#1a1a1a')
        ))

        # Subtitle/Meta Style
        self.styles.add(ParagraphStyle(
            name='AetherMeta',
            parent=self.styles['Normal'],
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#666666')
        ))

        # Heading 1 (Chapter)
        self.styles.add(ParagraphStyle(
            name='AetherH1',
            parent=self.styles['Heading1'],
            fontSize=18,
            leading=22,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2c3e50')
        ))

        # Body Text
        self.styles.add(ParagraphStyle(
            name='AetherBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=15,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        ))

        # Bullet Points
        self.styles.add(ParagraphStyle(
            name='AetherBullet',
            parent=self.styles['BodyText'],
            fontSize=11,
            leading=15,
            leftIndent=20,
            spaceAfter=5,
            bulletIndent=10
        ))

    def _add_cover_page(self, story: List, session_id: UUID):
        """Creates a branded cover page."""
        story.append(Spacer(1, 100))
        story.append(Paragraph("AetherDocs", self.styles['AetherTitle']))
        story.append(Paragraph("Common Book — Unified Study Guide", self.styles['AetherMeta']))
        story.append(Spacer(1, 30))
        story.append(Paragraph(
            f"Session: {str(session_id)[:8]}...",
            self.styles['AetherMeta']
        ))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['AetherMeta']
        ))
        story.append(Spacer(1, 50))
        story.append(Paragraph(
            "This document was automatically synthesized by the AetherDocs Fusion Engine, "
            "combining video transcripts, documents, and visual content into a single, "
            "comprehensive study resource.",
            self.styles['AetherMeta']
        ))
        story.append(PageBreak())

    def _parse_markdown_content(self, story: List, content: str):
        """Parses basic Markdown content into ReportLab Paragraph objects."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue

            # Check for Headers
            if line.startswith('# '):
                clean_text = line[2:].strip()
                story.append(Paragraph(clean_text, self.styles['AetherH1']))
            elif line.startswith('## '):
                clean_text = line[3:].strip()
                story.append(Paragraph(clean_text, self.styles['Heading2']))
            elif line.startswith('### '):
                clean_text = line[4:].strip()
                story.append(Paragraph(clean_text, self.styles['Heading3']))

            # Check for Bullet Points
            elif line.startswith('- ') or line.startswith('* '):
                clean_text = line[2:].strip()
                formatted_text = self._format_bold(clean_text)
                story.append(Paragraph(f"• {formatted_text}", self.styles['AetherBullet']))
            
            # Standard Body Text
            else:
                formatted_line = self._format_bold(line)
                story.append(Paragraph(formatted_line, self.styles['AetherBody']))

    def _format_bold(self, text: str) -> str:
        """
        Replaces **text** with <b>text</b> for ReportLab.
        Handles multiple occurrences.
        """
        parts = text.split('**')
        formatted = ""
        for i, part in enumerate(parts):
            if i % 2 == 0:
                formatted += part
            else:
                formatted += f"<b>{part}</b>"
        return formatted

    def _add_metrics_section(self, story: List, metrics: dict):
        """
        Adds the "Efficiency & Metrics" report to the PDF.
        """
        story.append(PageBreak())
        story.append(Paragraph("Efficiency & Metrics Report", self.styles['AetherTitle']))
        
        # 1. Evaluation Metrics
        story.append(Paragraph("1. Evaluation Metrics (Session Specific)", self.styles['AetherH1']))
        
        retrieval_acc = metrics.get('retrieval_accuracy', 'N/A')
        answer_quality = metrics.get('answer_quality', 'N/A')
        stats = metrics.get('processing_stats', {})
        
        metrics_text = (
            f"<b>Retrieval/Confidence Score:</b> {retrieval_acc}<br/>"
            f"<b>Semantic Density Score:</b> {answer_quality}<br/>"
            f"<b>Total Processed Segments:</b> {stats.get('transcription_segments', 0)}<br/>"
            f"<b>Unique Insights Extracted:</b> {stats.get('unique_insights', 0)}"
        )
        story.append(Paragraph(metrics_text, self.styles['AetherBody']))
        
        # 2. Confusion Matrix Proxy (Topic Heatmap)
        story.append(Paragraph("2. Content Distribution (Confusion Matrix Proxy)", self.styles['AetherH1']))
        story.append(Paragraph(
            "The following table shows the density of key technical topics detected across the extracted insights, "
            "acting as a proxy for classification accuracy.", 
            self.styles['AetherBody']
        ))
        
        topics = stats.get('topic_coverage', {})
        if topics:
            table_data = [['Topic', 'Frequency / Density']]
            for topic, count in topics.items():
                table_data.append([topic, str(count)])
            
            from reportlab.platypus import Table, TableStyle
            t = Table(table_data, colWidths=[200, 100])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
                ('GRID', (0,0), (-1,-1), 1, colors.black),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))
        else:
            story.append(Paragraph("<i>No significant technical topics detected in this session.</i>", self.styles['AetherBody']))

        # 3. Comparison
        story.append(Paragraph("3. Comparison vs. Standard RAG", self.styles['AetherH1']))
        comparison_text = metrics.get('comparison_text', "N/A")
        story.append(Paragraph(comparison_text, self.styles['AetherBody']))
        
        # 4. Ablation Study
        story.append(Paragraph("4. Ablation Study", self.styles['AetherH1']))
        ablation_text = metrics.get('ablation_text', "N/A")
        story.append(Paragraph(ablation_text, self.styles['AetherBody']))

    def generate(self, session_id: UUID, content: str, output_path: Path, metrics: dict = None) -> Path:
        """
        Main entry point. Builds the PDF and saves it to the artifacts folder.
        """
        try:
            # Ensure parent dir exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            story = []

            # 1. Add Cover Page
            self._add_cover_page(story, session_id)
            
            # 2. Add Content (Parsed from Markdown)
            self._parse_markdown_content(story, content)

            # 3. Add Metrics Section (if provided)
            if metrics:
                self._add_metrics_section(story, metrics)

            # 4. Build
            doc.build(story)
            
            logger.info(f"[{session_id}] PDF generated successfully at {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"[{session_id}] PDF Generation failed: {e}")
            raise RuntimeError(f"Could not write PDF document: {e}")