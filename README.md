Newton Smart Home — Quotation App

Overview
- Streamlit app to create quotations, invoices, and receipts.
- Excel-backed storage under `data/` and Word templates for document generation.
- Exports DOCX by default and converts to PDF using iLovePDF, with local fallbacks.

Run
- Install dependencies:
  - Windows PowerShell:
    - `pip install -r requirements.txt`
- Start app:
  - `streamlit run main.py`

DOCX → PDF Conversion
- Primary: iLovePDF API tool `officepdf` using your public key in `.streamlit/secrets.toml`.
- Local fallbacks (used automatically if iLovePDF fails):
  - Linux/Unix: LibreOffice (`soffice --headless`) if available in PATH.
  - Windows/macOS: `docx2pdf` (requires Microsoft Word), then tries LibreOffice if installed.

Linux Setup (LibreOffice)
- Install and verify `soffice`:
  - Ubuntu/Debian:
    - `sudo apt-get update`
    - `sudo apt-get install -y libreoffice`
  - RHEL/CentOS/Rocky:
    - `sudo yum install -y libreoffice`
  - Alpine:
    - `sudo apk add --no-cache libreoffice`
  - Verify:
    - `soffice --headless --version`

Secrets Configuration
- File: `.streamlit/secrets.toml`
```
[ilovepdf]
public = "YOUR_ILOVEPDF_PUBLIC_KEY"
# Optional: disable local fallbacks and use only iLovePDF
disable_local_fallback = false
```

Troubleshooting
- “PDF conversion failed.” with “PDF debug:” line shows root cause, e.g.:
  - Missing iLovePDF key → set `[ilovepdf].public` in secrets.
  - LibreOffice not found → install `libreoffice` so `soffice` is in PATH.
  - Linux note: `docx2pdf` is not supported on Linux without Word; we now prefer LibreOffice there.
  - Network timeouts → ensure outbound HTTPS access to `api.ilovepdf.com`.

Security Note
- This repo currently includes `.streamlit/secrets.toml` and `data/*.xlsx` by request.
- Consider rotating keys and removing secrets from history for production deployments.
# Newton Smart Home – Quotation App

Streamlit app to generate Quotations, Invoices, and Receipts with Excel-backed data and Word template export.

## Run Locally

```powershell
# From repo root
pip install -r requirements.txt
streamlit run main.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a public GitHub repository.
2. Go to https://share.streamlit.io and select your repo.
3. App entrypoint: `main.py` (Python 3.10+ recommended).
4. Add Streamlit secrets if needed in the cloud console (`[secrets]`).

Notes:
- The app auto-creates Excel files on first run for customers/products/records.
- Keep your Word templates in `data/`:
  - `data/quotation_template.docx`
  - `data/invoice_template.docx`
  - `data/receipt_template.docx`
- Runtime Excel data (`*.xlsx`) is ignored by Git (see `.gitignore`).

## Deploy to your own server (optional)
- Use `gunicorn` + `streamlit` or Docker. Minimal Dockerfile:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## Repository Structure (key paths)
- `main.py` – routing + global theme
- `pages_custom/` – pages: quotation, invoice, receipt, customers, products
- `data/` – Word templates and runtime Excel files
- `requirements.txt` – Python dependencies
