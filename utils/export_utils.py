import os
from io import BytesIO
from typing import Tuple, Optional

import pypandoc


def ensure_pandoc_available() -> None:
    """
    Ensure a working pandoc binary is available. If not, download a local copy.
    """
    try:
        _ = pypandoc.get_pandoc_path()
    except OSError:
        # Attempt to download a private copy (works on Streamlit Cloud too)
        pypandoc.download_pandoc()


def save_word_and_pdf(word_buffer: BytesIO, base_filename: str) -> Tuple[str, Optional[str]]:
    """Save DOCX to disk and convert to PDF via pandoc.

    Returns (word_path, pdf_path). If conversion fails, pdf_path is None.
    """
    output_folder = os.path.join("data", "generated")
    os.makedirs(output_folder, exist_ok=True)

    word_path = os.path.join(output_folder, f"{base_filename}.docx")
    pdf_path = os.path.join(output_folder, f"{base_filename}.pdf")

    # Save Word file
    with open(word_path, "wb") as f:
        f.write(word_buffer.getvalue())

    # Try conversion
    try:
        ensure_pandoc_available()
        pypandoc.convert_file(word_path, "pdf", outputfile=pdf_path)
    except Exception:
        pdf_path = None

    return word_path, pdf_path
