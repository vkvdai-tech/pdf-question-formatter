# app.py
import streamlit as st
import os
from processor import extract_raw_text, parse_and_clean_pdf
from pdf_generator import generate_clean_pdf

# Page configuration
st.set_page_config(
    page_title="PDF Question Formatter",
    page_icon="📄",
    layout="centered"
)

# App UI Header
st.title("📄 PDF Question Paper Formatter")
st.write(
    "Upload raw, messy PDFs (with table fragments, duplicate lines, or OCR errors) "
    "to automatically clean, deduplicate, and generate a standardized PDF document."
)

st.divider()

# File Upload Section
uploaded_file = st.file_uploader("Choose a raw PDF file", type=["pdf"])

if uploaded_file is not None:
    st.info(f"File uploaded: **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")
    
    # Process Button
    if st.button("🚀 Process & Format PDF", type="primary"):
        with st.spinner("Extracting text and parsing with AI..."):
            try:
                # 1. Extract raw text from uploaded PDF
                raw_text = extract_raw_text(uploaded_file)
                
                if not raw_text.strip():
                    st.error("Could not extract any text from the PDF. Please check if it's a scanned image without OCR.")
                    st.stop()
                
                # 2. Parse and clean raw text using LLM
                parsed_data = parse_and_clean_pdf(raw_text)
                
                # 3. Generate clean output PDF
                output_filename = f"cleaned_{uploaded_file.name}"
                generate_clean_pdf(parsed_data, output_path=output_filename)
                
                st.success("✨ Processing & PDF Formatting Complete!")
                
                # Expandable preview of extracted questions
                with st.expander("🔍 Preview Extracted Data"):
                    st.write(f"**Title:** {parsed_data.title}")
                    st.write(f"**Total Questions Extracted:** {len(parsed_data.questions)}")
                    
                    for idx, q in enumerate(parsed_data.questions, 1):
                        st.markdown(f"**Q{idx}. {q.question_text}**")
                        for opt in q.options:
                            status = "✅" if opt.is_correct else "⚪"
                            st.caption(f"{status} **{opt.label}:** {opt.text}")
                        if q.solution:
                            st.info(f"**Solution:** {q.solution}")
                        st.divider()
                
                # Download Button for the cleaned PDF
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="📥 Download Clean PDF",
                        data=file,
                        file_name=output_filename,
                        mime="application/pdf"
                    )

            except Exception as e:
                st.error(f"An error occurred while processing: {str(e)}")

st.divider()
st.caption("Built with Streamlit, OpenAI Structured Outputs, and ReportLab.")