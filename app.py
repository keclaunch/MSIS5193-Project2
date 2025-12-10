import streamlit as st
import ollama
from pypdf import PdfReader
from docx import Document
from bs4 import BeautifulSoup

def extract_text_from_file(uploaded_file) -> str:
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()
    suffix = name.split(".")[-1]

    if suffix == "txt":
        raw = uploaded_file.read()
        return raw.decode("utf-8", errors="ignore")

    if suffix == "pdf":
        reader = PdfReader(uploaded_file)
        text = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
        return "\n".join(text)

    if suffix == "docx":
        document = Document(uploaded_file)
        return "\n".join(p.text for p in document.paragraphs)

    if suffix in ("html", "htm"):
        raw = uploaded_file.read()
        try:
            html = raw.decode("utf-8")
        except UnicodeDecodeError:
            html = raw.decode("latin-1", errors="ignore")
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n")

    return ""


def ask_ollama(question: str, context: str) -> str:
    context = context[:15000]  # simple safety limit
    system_prompt = (
        "You are a helpful assistant. When document context is provided, "
        "base your answer primarily on that context. If the context does not "
        "contain the answer, say so and answer from your general knowledge."
    )

    user_content = f"Question:\n{question}\n\nDocument context:\n{context}"

    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return response["message"]["content"]

st.set_page_config(page_title="Input to AI", layout="centered")

st.title("Input to AI")

question = st.text_input("Enter your question:")

uploaded_file = st.file_uploader(
    "Upload attachment (optional):",
    type=["txt", "pdf", "docx", "html", "htm"],
)

if st.button("Submit"):
    if not question.strip():
        st.error("Please enter a question before submitting.")
    else:
        with st.spinner("Thinking..."):
            context_text = extract_text_from_file(uploaded_file)
            answer = ask_ollama(question, context_text)

        st.markdown("## AI Response:")
        st.write(answer)
