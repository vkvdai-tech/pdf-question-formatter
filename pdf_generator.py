# pdf_generator.py
import html
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether

def safe_str(val):
    if val is None:
        return ""
    return html.escape(str(val))

def generate_clean_pdf(question_paper):
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
        fontSize=10,
        leading=14,
        spaceAfter=4
    )
    opt_style = ParagraphStyle(
        'OptionText',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        leftIndent=12,
        spaceAfter=3
    )
    sol_style = ParagraphStyle(
        'SolText',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        spaceAfter=6
    )

    story = []
    
    # Paper Header
    paper_title = safe_str(getattr(question_paper, 'title', 'Question Paper'))
    story.append(Paragraph(f"<b>{paper_title}</b>", title_style))
    story.append(Spacer(1, 10))
    
    questions = getattr(question_paper, 'questions', []) or []
    global_q_counter = 1

    for q in questions:
        q_elements = []
        
        # Raw text extraction
        q_text = str(getattr(q, 'question_text', '') or getattr(q, 'text', '') or '')
        
        # Check if multiple sub-questions were merged into this single text block
        sub_questions = re.split(r'\n(?=\d+\.\s)', q_text)
        
        for sub_idx, sub_q in enumerate(sub_questions):
            sub_q_clean = safe_str(sub_q.strip())
            if not sub_q_clean:
                continue
            
            # Formatting question header
            q_num_label = f"Q{global_q_counter}"
            global_q_counter += 1
            
            q_elements.append(Paragraph(f"<b>{q_num_label}.</b> {sub_q_clean}", q_style))
            
            # Options
            options = getattr(q, 'options', []) or []
            # Only append options for the main or relevant question sub-part
            if sub_idx == len(sub_questions) - 1 or len(sub_questions) == 1:
                for opt in options:
                    lbl = safe_str(getattr(opt, 'label', '') or getattr(opt, 'key', ''))
                    txt = safe_str(getattr(opt, 'text', '') or getattr(opt, 'option_text', ''))
                    q_elements.append(Paragraph(f"<b>({lbl})</b> {txt}", opt_style))
            
            # Solution / Explanation
            sol = getattr(q, 'solution', None) or getattr(q, 'explanation', None)
            if sol and (sub_idx == len(sub_questions) - 1 or len(sub_questions) == 1):
                q_elements.append(Paragraph(f"<b>Solution:</b> <i>{safe_str(sol)}</i>", sol_style))
            
            q_elements.append(Spacer(1, 6))

        story.append(KeepTogether(q_elements))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

generate_pdf = generate_clean_pdf