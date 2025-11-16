import io
import os
import tempfile
import requests
import streamlit as st
from typing import Optional
from streamlit.components.v1 import html as st_html
import base64

ILOVEPDF_AUTH_URL = "https://api.ilovepdf.com/v1/auth"
ILOVEPDF_CREATE_TASK_URL = "https://api.ilovepdf.com/v1/create-task"


def _record_error(msg: str):
    st.session_state["ilovepdf_last_error"] = msg


def _try_local_docx2pdf(docx_bytes: bytes, filename: str) -> Optional[bytes]:
    """Fallback using docx2pdf (requires MS Word, Windows/Mac)."""
    # Allow disabling fallback via secrets flag
    if st.secrets.get("ilovepdf", {}).get("disable_local_fallback", False):
        _record_error("Local fallback disabled by secrets flag.")
        return None
    try:
        from docx2pdf import convert  # type: ignore
    except Exception:
        _record_error("Fallback docx2pdf not available (module missing).")
        return None
    # On Windows docx2pdf needs COM initialisation (pywin32 / pythoncom)
    com_inited = False
    try:
        if os.name == "nt":
            try:
                import pythoncom  # type: ignore
                pythoncom.CoInitialize()
                com_inited = True
            except Exception as e:
                _record_error(f"Failed COM init for docx2pdf: {e}")
        with tempfile.TemporaryDirectory() as tmp:
            docx_path = os.path.join(tmp, f"{filename}.docx")
            pdf_path = os.path.join(tmp, f"{filename}.pdf")
            with open(docx_path, "wb") as f:
                f.write(docx_bytes)
            convert(docx_path, pdf_path)
            if not os.path.exists(pdf_path):
                _record_error("docx2pdf produced no output file.")
                return None
            return open(pdf_path, "rb").read()
    except Exception as e:
        _record_error(f"docx2pdf fallback failed: {e}")
        return None
    finally:
        if com_inited:
            try:
                import pythoncom  # type: ignore
                pythoncom.CoUninitialize()
            except Exception:
                pass


def convert_docx_to_pdf_ilovepdf(docx_bytes: bytes, filename: str) -> Optional[bytes]:
    """Convert DOCX bytes to PDF via iLovePDF; fallback to local docx2pdf.

    Detailed error stored in st.session_state['ilovepdf_last_error'].
    """
    st.session_state.pop("ilovepdf_last_error", None)
    try:
        public_key = st.secrets["ilovepdf"]["public"]
    except Exception:
        _record_error("Missing ilovepdf public key in secrets.")
        return _try_local_docx2pdf(docx_bytes, filename)

    # --- iLovePDF remote flow ---
    try:
        # 1. Auth (only public_key needed per API spec)
        auth_resp = requests.post(ILOVEPDF_AUTH_URL, json={"public_key": public_key}, timeout=30)
        if auth_resp.status_code != 200:
            _record_error(f"Auth failed ({auth_resp.status_code}): {auth_resp.text[:120]}")
            return _try_local_docx2pdf(docx_bytes, filename)
        token = auth_resp.json().get("token")
        if not token:
            _record_error("Token missing in auth response.")
            return _try_local_docx2pdf(docx_bytes, filename)
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create task
        task_resp = requests.post(ILOVEPDF_CREATE_TASK_URL, json={"tool": "officepdf"}, headers=headers, timeout=30)
        if task_resp.status_code != 200:
            _record_error(f"Create task failed ({task_resp.status_code}): {task_resp.text[:120]}")
            return _try_local_docx2pdf(docx_bytes, filename)
        tj = task_resp.json()
        task_id = tj.get("task")
        server = tj.get("server")
        if not task_id or not server:
            _record_error("Task or server missing in create-task response.")
            return _try_local_docx2pdf(docx_bytes, filename)

        # 3. Upload (field must be files[] per API docs)
        upload_url = f"https://{server}/v1/upload"
        file_stream = io.BytesIO(docx_bytes)
        files = {"files[]": (f"{filename}.docx", file_stream, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        form_data = {"task": task_id}
        up_resp = requests.post(upload_url, files=files, data=form_data, headers=headers, timeout=120)
        if up_resp.status_code != 200:
            _record_error(f"Upload failed ({up_resp.status_code}): {up_resp.text[:120]}")
            return _try_local_docx2pdf(docx_bytes, filename)

        # 4. Process (must include tool)
        process_url = f"https://{server}/v1/process"
        proc_payload = {"task": task_id, "tool": "officepdf"}
        proc_resp = requests.post(process_url, json=proc_payload, headers=headers, timeout=180)
        if proc_resp.status_code != 200:
            _record_error(f"Process failed ({proc_resp.status_code}): {proc_resp.text[:120]}")
            return _try_local_docx2pdf(docx_bytes, filename)

        # 5. Download
        download_url = f"https://{server}/v1/download/{task_id}"
        dl_resp = requests.get(download_url, headers=headers, timeout=180)
        if dl_resp.status_code != 200:
            _record_error(f"Download failed ({dl_resp.status_code}): {dl_resp.text[:120]}")
            return _try_local_docx2pdf(docx_bytes, filename)

        return dl_resp.content
    except requests.Timeout:
        _record_error("iLovePDF network timeout; switching to local fallback.")
        return _try_local_docx2pdf(docx_bytes, filename)
    except Exception as e:
        _record_error(f"Unexpected iLovePDF error: {e}; trying local fallback.")
        return _try_local_docx2pdf(docx_bytes, filename)


def trigger_dual_downloads(docx_bytes: bytes, pdf_bytes: Optional[bytes], docx_name: str, pdf_name: Optional[str] = None):
    """Trigger two downloads (DOCX then PDF) automatically via a hidden HTML component.

    - Does not add visible UI buttons.
    - Respects user's single-click flow. If PDF bytes are None, only DOCX is downloaded.
    """
    try:
        b64_docx = base64.b64encode(docx_bytes).decode()
        mime_docx = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        js_pdf = ""
        if pdf_bytes:
            b64_pdf = base64.b64encode(pdf_bytes).decode()
            mime_pdf = "application/pdf"
            pdf_name = pdf_name or "file.pdf"
            js_pdf = f"""
                const a2 = document.createElement('a');
                a2.href = 'data:{mime_pdf};base64,{b64_pdf}';
                a2.download = '{pdf_name}';
                document.body.appendChild(a2);
                setTimeout(()=>{{ a2.click(); a2.remove(); }}, 350);
            """.replace("{mime_pdf}", mime_pdf).replace("{b64_pdf}", b64_pdf).replace("{pdf_name}", pdf_name)

        html_snippet = f"""
        <div id='auto-dl' style='display:none;'></div>
        <script>
            const a1 = document.createElement('a');
            a1.href = 'data:{mime_docx};base64,{b64_docx}';
            a1.download = '{docx_name}';
            document.body.appendChild(a1);
            a1.click();
            a1.remove();
            {js_pdf}
        </script>
        """.replace("{mime_docx}", mime_docx).replace("{b64_docx}", b64_docx).replace("{docx_name}", docx_name)

        st_html(html_snippet, height=0)
    except Exception as e:
        _record_error(f"Auto-download render error: {e}")

    # end function
