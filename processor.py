# processor.py
import os
from pypdf import PdfReader
from openai import OpenAI
from schema import QuestionPaper

# Load API key from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_raw_text(pdf_file) -> str:
    """Extracts raw text page by page from an uploaded PDF file."""
    reader = PdfReader(pdf_file)
    extracted_text = ""
    
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            extracted_text += f"\n--- Page {page_num} ---\n" + text
            
    return extracted_text

def parse_and_clean_pdf(raw_text: str) -> QuestionPaper:
    """Uses LLM with Structured Output to clean, deduplicate, and format raw text."""
    
    system_prompt = (
        "You are an expert exam paper editor and data parser. "
        "You will receive raw text extracted from a PDF that contains multiple-choice questions. "
        "The raw text is noisy, contains duplicate text blocks, broken line wraps, and pipe characters (|) "
        "from bad PDF table extractions.\n\n"
        "Your Job:\n"
        "1. Identify distinct questions and clean up duplicated or repeated phrases.\n"
        "2. Extract the question text clearly without repetitive lines.\n"
        "3. Parse options (e.g., Option 1, Option 2 or a, b, c) and identify which option is marked as 'Correct' or 'Incorrect'.\n"
        "4. Extract solutions/explanations if present, as well as positive and negative marks.\n"
        "5. Output the result strictly following the provided schema."
    )

    user_prompt = f"Here is the raw PDF text to clean and structure:\n\n{raw_text}"

    # Utilizing OpenAI's Structured Output parsing method
    response = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format=QuestionPaper,
    )

    return response.choices[0].message.parsed


# Quick local test block
if __name__ == "__main__":
    print("Processor module ready!")