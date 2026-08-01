# processor.py
import os
from pypdf import PdfReader
from openai import OpenAI
from schema import QuestionPaper, Question  # Adjust import based on your exact schema

client = OpenAI()

def parse_and_clean_pdf(pdf_file, chunk_size=3):
    """
    Extracts text page by page, sends small page batches to OpenAI,
    and combines all parsed questions into a single QuestionPaper.
    """
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)
    
    all_questions = []
    
    # Process the PDF in small page chunks (e.g., 3 pages at a time)
    for i in range(0, total_pages, chunk_size):
        chunk_pages = reader.pages[i:i + chunk_size]
        chunk_text = "\n".join([page.extract_text() or "" for page in chunk_pages])
        
        if not chunk_text.strip():
            continue
            
        prompt = f"""
        Extract all questions and options from the following text into structured format.
        DO NOT skip, omit, or summarize any questions. Extract EVERY single question completely.
        
        TEXT:
        {chunk_text}
        """

        # Call OpenAI Structured Outputs for this chunk
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",  # or gpt-4o
            messages=[
                {"role": "system", "content": "You are a precise exam question extractor."},
                {"role": "user", "content": prompt}
            ],
            response_format=QuestionPaper,
        )

        parsed_chunk = completion.choices[0].message.parsed
        
        # Collect questions from this chunk
        if parsed_chunk and hasattr(parsed_chunk, 'questions'):
            all_questions.extend(parsed_chunk.questions)

    # Return a consolidated QuestionPaper object containing all extracted questions
    return QuestionPaper(questions=all_questions)