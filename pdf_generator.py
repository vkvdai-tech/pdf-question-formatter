# pdf_generator.py
import html
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

def safe_str(val):
    if val is None:
        return ""
    return html.escape(str(val))

def generate_clean_pdf(question_paper):  # <-- Renamed to match app.py
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'PaperTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=12
    )
    q_style = ParagraphStyle(
        'QuestionText',
        parent=styles['Normal'],
        fontSize=11,
        leading=15,
        spaceAfter=6
    )
    opt_style = ParagraphStyle(
        'OptionText',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        leftIndent=15,
        spaceAfter=4
    )
    
    story = []
    
    # Title
    paper_title = safe_str(getattr(question_paper, 'title', 'Question Paper'))
    story.append(Paragraph(f"<b>{paper_title}</b>", title_style))
    story.append(Spacer(1, 12))
    
    # Process Questions
    questions = getattr(question_paper, 'questions', []) or []
    for idx, q in enumerate(questions, 1):
        q_elements = []
        
        # Question Header/Text
        q_num = safe_str(getattr(q, 'question_number', None) or getattr(q, 'number', None) or f"Q{idx}")
        q_text = safe_str(getattr(q, 'question_text', '') or getattr(q, 'text', ''))
        q_elements.append(Paragraph(f"<b>{q_num}.</b> {q_text}", q_style))
        
        # Options
        options = getattr(q, 'options', []) or []
        for opt in options:
            lbl = safe_str(getattr(opt, 'label', '') or getattr(opt, 'key', ''))
            txt = safe_str(getattr(opt, 'text', '') or getattr(opt, 'option_text', ''))
            q_elements.append(Paragraph(f"<b>({lbl})</b> {txt}", opt_style))
        
        # Solution / Explanation
        sol = getattr(q, 'solution', None) or getattr(q, 'explanation', None)
        if sol:
            q_elements.append(Paragraph(f"<i>Solution: {safe_str(sol)}</i>", opt_style))
            
        q_elements.append(Spacer(1, 10))
        story.append(KeepTogether(q_elements))
        
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Alias just in case app.py references generate_pdf anywhere else
generate_pdf = generate_clean_pdf