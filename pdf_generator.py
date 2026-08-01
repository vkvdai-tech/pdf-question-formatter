# pdf_generator.py
import html
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether

def safe_str(val):
    if val is None:
        return ""
    return html.escape(str(val).strip())

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
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=9.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#000000')
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#000000')
    )

    story = []
    questions = getattr(question_paper, 'questions', []) or []

    for idx, q in enumerate(questions, 1):
        # Extract text values
        q_text = safe_str(getattr(q, 'question_text', '') or getattr(q, 'text', ''))
        q_type = safe_str(getattr(q, 'question_type', 'multiple_Choice') or 'multiple_Choice')
        solution = safe_str(getattr(q, 'solution', '') or getattr(q, 'explanation', ''))
        
        # Build exact 2-column table structure matching economy pdf
        table_data = [
            [Paragraph("<b>Question</b>", label_style), Paragraph(q_text, cell_style)],
            [Paragraph("<b>Type</b>", label_style), Paragraph(q_type, cell_style)],
        ]

        # Append Options
        options = getattr(q, 'options', []) or []
        for opt_idx, opt in enumerate(options, 1):
            lbl = safe_str(getattr(opt, 'label', '') or getattr(opt, 'key', '') or f"Option {opt_idx}")
            txt = safe_str(getattr(opt, 'text', '') or getattr(opt, 'option_text', ''))
            
            # Format label column like 'Option 1', 'Option 2' or 'a', 'b'
            option_label = f"Option {lbl}" if len(lbl) == 1 and lbl.isdigit() else f"Option ({lbl})" if len(lbl) == 1 else lbl
            table_data.append([
                Paragraph(f"<b>{option_label}</b>", label_style),
                Paragraph(txt, cell_style)
            ])

        # Append Solution Row
        if solution:
            table_data.append([
                Paragraph("<b>Solution</b>", label_style),
                Paragraph(solution, cell_style)
            ])

        # Append Marks Row
        table_data.append([
            Paragraph("<b>Marks</b>", label_style),
            Paragraph("1 &nbsp;&nbsp;&nbsp; 0.33", cell_style)
        ])

        # Create ReportLab Table (Column 1 = 100px, Column 2 = 450px)
        q_table = Table(table_data, colWidths=[100, 450])
        q_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#64748B')),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAFC')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))

        story.append(KeepTogether([q_table, Spacer(1, 14)]))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

generate_pdf = generate_clean_pdf