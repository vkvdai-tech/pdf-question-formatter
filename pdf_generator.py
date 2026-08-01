# pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from schema import QuestionPaper

def generate_clean_pdf(data: QuestionPaper, output_path: str = "formatted_output.pdf") -> str:
    """Renders the structured QuestionPaper data into table blocks matching the raw economy PDF style."""
    
    # Page Setup (Letter Size, 0.5 inch margins)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    # Define Paragraph Styles for Table Cells
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#111111')
    )
    
    text_style = ParagraphStyle(
        'TableCellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#222222')
    )
    
    correct_style = ParagraphStyle(
        'CorrectText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#27AE60')
    )
    
    incorrect_style = ParagraphStyle(
        'IncorrectText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#7F8C8D')
    )

    elements = []

    # Process each question into an individual structured Table
    for q in data.questions:
        table_data = []
        
        # Row 1: Question Header & Text
        table_data.append([
            Paragraph("<b>Question</b>", header_style),
            Paragraph(q.question_text, text_style)
        ])
        
        # Row 2: Question Type
        table_data.append([
            Paragraph("<b>Type</b>", header_style),
            Paragraph(q.question_type, text_style)
        ])
        
        # Rows for Options
        for opt in q.options:
            status_paragraph = Paragraph("Correct.", correct_style) if opt.is_correct else Paragraph("Incorrect.", incorrect_style)
            table_data.append([
                Paragraph(f"<b>{opt.label}</b>", header_style),
                Paragraph(opt.text, text_style),
                status_paragraph
            ])
            
        # Row for Solution (if available)
        if q.solution:
            table_data.append([
                Paragraph("<b>Solution</b>", header_style),
                Paragraph(q.solution, text_style)
            ])
            
        # Row for Marks
        marks_str = f"Positive: {q.marks} | Negative: {q.negative_marks}"
        table_data.append([
            Paragraph("<b>Marks</b>", header_style),
            Paragraph(marks_str, text_style)
        ])
        
        # Define 2-column and 3-column span layouts for ReportLab Table
        # Default col widths: Col 0 = 90pt, Col 1 = 360pt, Col 2 = 90pt (Total: 540pt printable width)
        col_widths = [90, 360, 90]
        
        # Table Styling Rules (Grid borders, light backgrounds)
        t_style = [
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CCCCCC')),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#F8F9F9')), # Gray background for headers column
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]
        
        # Span columns across for rows that don't need 3 columns (e.g. Question, Type, Solution, Marks)
        row_idx = 0
        
        # Span Question Row
        t_style.append(('SPAN', (1, row_idx), (2, row_idx)))
        row_idx += 1
        
        # Span Type Row
        t_style.append(('SPAN', (1, row_idx), (2, row_idx)))
        row_idx += 1
        
        # Skip Option Rows (they use all 3 columns: Label, Text, Correct/Incorrect)
        row_idx += len(q.options)
        
        # Span Solution Row (if present)
        if q.solution:
            t_style.append(('SPAN', (1, row_idx), (2, row_idx)))
            row_idx += 1
            
        # Span Marks Row
        t_style.append(('SPAN', (1, row_idx), (2, row_idx)))

        # Create Table Object
        q_table = Table(table_data, colWidths=col_widths, style=TableStyle(t_style))
        
        elements.append(q_table)
        elements.append(Spacer(1, 15)) # Space between question tables

    # Build PDF
    doc.build(elements)
    return output_path


if __name__ == "__main__":
    print("Updated PDF Generator ready!")