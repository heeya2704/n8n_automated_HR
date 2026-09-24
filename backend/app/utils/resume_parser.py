import os
from pypdf import PdfReader
import docx

def extract_text_from_file(filepath: str) -> str:
    """
    Extracts text from PDF, DOCX, or TXT file.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text.strip()
    elif ext == ".docx":
        doc = docx.Document(filepath)
        text = [para.text for para in doc.paragraphs]
        return "\n".join(text).strip()
    elif ext in [".txt", ".md"]:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    else:
        raise ValueError(f"Unsupported resume file extension: {ext}")
