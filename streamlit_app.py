import streamlit as st
from openai import OpenAI
import fitz

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – GPT will answer! "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Upload PDF file
    uploaded_file = st.file_uploader("📤 Upload a PDF document", type=["pdf"])

    # Extract text from PDF
    document_text = ""
    if uploaded_file is not None:
        try:
            with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
                for page in doc:
                    document_text += page.get_text()
        except Exception as e:
            st.error(f"Error reading PDF: {e}")

    # Ask the user for a question via `st.text_area`.
    question = st.text_area(
        "Now ask a question about the document!",
        placeholder="Can you give me a short summary?",
        disabled=not uploaded_file,
    )



    if uploaded_file and question:

        # Process the uploaded file and question.
        document = uploaded_file.read().decode()
        messages = [
            {
                "role": "user",
                "content": f"Here's a document: {document} \n\n---\n\n {question}",
            }
        ]

try:
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Consider switching to "gpt-3.5-turbo" if on "gpt-4"
        messages=messages,
        stream=True,
    )
    st.write_stream(stream)

except openai.RateLimitError:
    st.error("⚠️ You have hit your OpenAI rate limit. Please wait and try again later.")
