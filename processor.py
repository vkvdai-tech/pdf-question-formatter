# processor.py
import os
from pypdf import PdfReader
from openai import OpenAI
from schema import QuestionPaper, Question

client = OpenAI()

def parse_and_clean_pdf(pdf_file, chunk_size=3, progress_callback=None):
    """
    Processes large PDFs in page batches (chunks) to easily handle 100+ pages
    without exceeding AI context window or output token limits.
    """
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)
    all_questions = []

    # Calculate total chunk iterations
    total_chunks = (total_pages + chunk_size - 1) // chunk_size

    for chunk_index, i in enumerate(range(0, total_pages, chunk_size)):
        chunk_pages = reader.pages[i:i + chunk_size]
        chunk_text = "\n".join([page.extract_text() or "" for page in chunk_pages])

        # Report progress back to Streamlit
        if progress_callback:
            progress = (chunk_index + 1) / total_chunks
            current_page_end = min(i + chunk_size, total_pages)
            progress_callback(
                progress, 
                f"Processing pages {i + 1} to {current_page_end} of {total_pages}..."
            )

        # Skip blank/empty pages
        if not chunk_text.strip():
            continue

        prompt = f"""
        Extract all exam/test questions and options from the following text.
        CRITICAL: DO NOT skip, summarize, or omit any questions. Extract EVERY question completely.

        TEXT TO EXTRACT FROM:
        {chunk_text}
        """

        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a precise exam question extractor."},
                    {"role": "user", "content": prompt}
                ],
                response_format=QuestionPaper,
            )

            parsed_chunk = completion.choices[0].message.parsed
            if parsed_chunk and hasattr(parsed_chunk, 'questions'):
                all_questions.extend(parsed_chunk.questions)

        except Exception as e:
            print(f"Warning: Failed to process pages {i + 1} to {i + chunk_size}: {e}")
            continue

    return QuestionPaper(questions=all_questions)