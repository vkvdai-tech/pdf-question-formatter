# processor.py
import json
from typing import List, Dict, Any
from pypdf import PdfReader
from openai import OpenAI
import streamlit as st
from schema import QuestionPaper

# Initialize OpenAI Client (using Streamlit Secrets or Environment Variable)
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))

EXTRACTION_SYSTEM_PROMPT = """
You are a precise data extraction engine. Your task is to extract all exam questions from the provided text into the structured QuestionPaper schema.

CRITICAL EXTRACTION RULES:
1. COMPLETE TEXT PRESERVATION: Capture the FULL text of every question. For statement-based questions (e.g., "1. Statement A... 2. Statement B... Which of the statements given above is/are correct?"), you MUST preserve all numbered statements completely in 'question_text'. Never truncate or drop statements.
2. DEDUPING: If the exact same question block or prompt is repeated twice back-to-back in the raw input text, extract it ONCE cleanly.
3. PRESERVE ALL QUESTIONS: Extract every single question present in the text sequentially. Do not skip or omit any questions.
4. OPTION EXTRACTION: Extract options into labels (a, b, c, d or 1, 2, 3, 4) and clean option text. Keep 'is_correct' as true/false if indicated in the input.
5. SOLUTION/EXPLANATION: Include the complete explanation, solution, or rationale into the 'solution' field.
"""

def extract_text_from_pdf(pdf_file) -> List[str]:
    """Reads PDF and returns a list of page texts."""
    reader = PdfReader(pdf_file)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    return pages_text


def chunk_pages(pages_text: List[str], chunk_size: int = 3) -> List[str]:
    """Segments pages into chunks of `chunk_size` (default: 3 pages) to stay within context limits."""
    chunks = []
    for i in range(0, len(pages_text), chunk_size):
        chunk_text = "\n--- PAGE BREAK ---\n".join(pages_text[i:i + chunk_size])
        chunks.append(chunk_text)
    return chunks


def process_chunk(chunk_text: str) -> QuestionPaper:
    """Sends a single chunk to OpenAI gpt-4o-mini using Structured Outputs."""
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Extract all questions from the following text:\n\n{chunk_text}"}
        ],
        response_format=QuestionPaper,
        temperature=0.1
    )
    return response.choices[0].message.parsed


def process_pdf(pdf_file) -> QuestionPaper:
    """
    Main processing loop:
    1. Extracts text from PDF
    2. Chunks text into 3-page segments
    3. Batches calls to OpenAI Structured Outputs
    4. Combines results into a single consolidated QuestionPaper object
    """
    pages_text = extract_text_from_pdf(pdf_file)
    if not pages_text:
        raise ValueError("Could not extract any readable text from the provided PDF.")

    chunks = chunk_pages(pages_text, chunk_size=3)
    
    combined_questions = []
    paper_title = "Question Paper"

    # Process each chunk sequentially
    progress_bar = st.progress(0)
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks):
        try:
            parsed_paper = process_chunk(chunk)
            if parsed_paper and parsed_paper.questions:
                combined_questions.extend(parsed_paper.questions)
                if parsed_paper.title and paper_title == "Question Paper":
                    paper_title = parsed_paper.title
        except Exception as e:
            st.warning(f"Warning: Issue processing chunk {idx + 1}/{total_chunks}: {str(e)}")
        
        # Update Streamlit progress bar
        progress_bar.progress((idx + 1) / total_chunks)

    progress_bar.empty()

    # Re-number questions sequentially to ensure continuous Q1, Q2, Q3... numbering
    for idx, q in enumerate(combined_questions, 1):
        q.question_number = str(idx)

    return QuestionPaper(
        title=paper_title,
        questions=combined_questions
    )