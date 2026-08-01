# app.py
import streamlit as st
import io
from processor import process_pdf
from pdf_generator import generate_clean_pdf

st.set_page_config(page_title="PDF Question Bank Formatter", layout="centered")

st.title("📄 PDF Question Bank Formatter")
st.write("Upload a raw or poorly formatted question PDF to generate a clean, structured PDF using AI.")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

if uploaded_file is not None:
    if st.button("Process & Format PDF", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(progress, text):
            progress_bar.progress(progress)
            status_text.text(text)

        try:
            # 1. Parse PDF using chunking
            parsed_paper = parse_and_clean_pdf(uploaded_file, chunk_size=3, progress_callback=update_progress)

            status_text.text("Generating formatted PDF document...")
            
            # 2. Generate PDF using ReportLab
            pdf_bytes = generate_clean_pdf(parsed_paper)

            progress_bar.progress(1.0)
            status_text.empty()
            st.success(f"Success! Extracted {len(parsed_paper.questions)} questions across all pages.")

            # 3. Provide Download Button
            st.download_button(
                label="📥 Download Formatted PDF",
                data=pdf_bytes,
                file_name="formatted_question_paper.pdf",
                mime="application/pdf"
            )

        except Exception as e:
            st.error(f"An error occurred while processing the PDF: {e}")