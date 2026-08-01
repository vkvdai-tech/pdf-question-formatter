# pdf_generator.py
import html
import re
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

def safe_str(val):
    if val is None:
        return ""
    # Strip duplicate lines if raw text was duplicated in input
    lines = str(val).split('\n')
    deduped = []
    for line in lines:
        line_clean = line.strip()
        if line_clean and line_clean not in deduped:
            deduped.append(line_clean)
    return html.escape(" ".join(deduped))

def generate_clean_pdf(question_paper):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )
    
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        fontName='Helvetica-Bold',
        textColor=colors.whitesmoke
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13
    )
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=9.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1E293B')
    )

    story = []
    questions = getattr(question_paper, 'questions', []) or []

    for idx, q in enumerate(questions, 1):
        # Extract and sanitize unique question data
        q_text = safe_str(getattr(q, 'question_text', '') or getattr(q, 'text', ''))
        q_type = safe_str(getattr(q, 'question_type', 'multiple_Choice'))
        solution = safe_str(getattr(q, 'solution', '') or getattr(q, 'explanation', ''))
        
        # Build Table Grid Rows
        table_data = [
            # Header Row
            [Paragraph(f"Question #{idx}", header_style), Paragraph(f"Type: {q_type}", header_style)],
            
            # Question Body Row
            [Paragraph("<b>Question</b>", label_style), Paragraph(q_text, cell_style)],
        ]

        # Add Options cleanly
        options = getattr(q, 'options', []) or []
        for opt in options:
            lbl = safe_str(getattr(opt, 'label', '') or getattr(opt, 'key', ''))
            txt = safe_str(getattr(opt, 'text', '') or getattr(opt, 'option_text', ''))
            is_corr = getattr(opt, 'is_correct', False)
            status = " <font color='green'><b>(Correct)</b></font>" if is_corr else ""
            
            table_data.append([
                Paragraph(f"Option ({lbl})", label_style),
                Paragraph(f"{txt}{status}", cell_style)
            ])

        # Solution / Explanation Row
        if solution:
            table_data.append([
                Paragraph("<b>Solution</b>", label_style),
                Paragraph(solution, cell_style)
            ])

        # Create Table Object
        # Column 1 = 110px (Fixed Labels), Column 2 = 440px (Dynamic Content)
        q_table = Table(table_data, colWidths=[110, 440])
        
        # Grid Styling
        q_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#1E293B')), # Dark Header
            ('TEXTCOLOR', (0, 0), (1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')), # Table border lines
            ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#F8FAFC')), # Light grey for label column
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(KeepTogether([q_table, Spacer(1, 14)]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

generate_pdf = generate_clean_pdf