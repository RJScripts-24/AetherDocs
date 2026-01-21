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

    def generate(self, session_id: UUID, content: str, output_path: Path) -> Path:
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

            # 3. Build
            doc.build(story)
            
            logger.info(f"[{session_id}] PDF generated successfully at {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"[{session_id}] PDF Generation failed: {e}")
            raise RuntimeError(f"Could not write PDF document: {e}")

    def _add_cover_page(self, story: List, session_id: UUID):
        """Constructs the cover page."""
        # Logo could go here if available: story.append(Image('assets/logo.png'))
        story.append(Spacer(1, 100))
        
        title = "The Common Book"
        story.append(Paragraph(title, self.styles['AetherTitle']))
        
        story.append(Spacer(1, 12))
        subtitle = "Unified Intelligence Report"
        story.append(Paragraph(subtitle, self.styles['AetherMeta']))
        
        story.append(Spacer(1, 50))
        
        # Session Metadata
        timestamp = datetime.now().strftime("%B %d, %Y • %H:%M")
        meta_info = f"Session ID: {str(session_id)[:8]}...<br/>Generated on: {timestamp}"
        story.append(Paragraph(meta_info, self.styles['AetherMeta']))
        
        story.append(PageBreak())

    def _parse_markdown_content(self, story: List, text: str):
        """
        A lightweight Markdown parser to map LLM output to ReportLab styles.
        """
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue

            # Check for Headers
            if line.startswith('# '):
                # H1
                clean_text = line[2:].strip()
                story.append(Paragraph(clean_text, self.styles['AetherH1']))
            elif line.startswith('## '):
                # H2 (Map to H1 style for simplicity, or define H2)
                clean_text = line[3:].strip()
                story.append(Paragraph(clean_text, self.styles['Heading2']))
            elif line.startswith('### '):
                # H3
                clean_text = line[4:].strip()
                story.append(Paragraph(clean_text, self.styles['Heading3']))
            
            # Check for Bullet Points
            elif line.startswith('- ') or line.startswith('* '):
                clean_text = line[2:].strip()
                # Use a bullet character
                story.append(Paragraph(f"• {clean_text}", self.styles['AetherBullet']))
            
            # Standard Body Text
            else:
                # Basic bold parsing (**text**)
                # ReportLab supports HTML-like tags <b>...</b>
                formatted_line = line.replace('**', '<b>', 1).replace('**', '</b>', 1)
                story.append(Paragraph(formatted_line, self.styles['AetherBody']))