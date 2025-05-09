import streamlit as st
from openai import OpenAI
import fitz  # PyMuPDF

# Show title and description
st.title("📄 PDF Document Question Answering")
st.write(
    "Upload a PDF document and ask a question – GPT will answer using the content of the file! "
    "You need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Ask for API key
openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create client
    client = OpenAI(api_key=openai_api_key)

    # Upload PDF
    uploaded_file = st.file_uploader("📤 Upload a PDF document", type=["pdf"])

    # Extract text
    document_text = ""
    if uploaded_file:
        try:
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                for page in doc:
                    document_text += page.get_text()
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

    # Ask a question
    question = st.text_area(
        "📝 Ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not document_text,
    )

    # Process Q&A
    if document_text and question:
        messages = [
            {
                "role": "user",
                "content": f"Here's a document:\n{document_text}\n\n---\n\n{question}",
            }
        ]

        try:
            # Generate answer
            stream = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                stream=True,
            )
            st.write_stream(stream)

        except Exception as e:
            if "RateLimitError" in str(e):
                st.error("⚠️ You have hit your OpenAI rate limit. Please wait and try again later.")
            elif "AuthenticationError" in str(e):
                st.error("⚠️ Invalid OpenAI API key. Please check and try again.")
            else:
                st.error(f"⚠️ An unexpected error occurred: {e}")
