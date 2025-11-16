import io
import os
import platform
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


def _get_ilovepdf_public_key() -> Optional[str]:
    """Retrieve iLovePDF public key from st.secrets, otherwise fallback to data/stream.toml.

    Streamlit only populates st.secrets from .streamlit/secrets.toml (or host secrets).
    For portability, we also try reading a project file at data/stream.toml when secrets
    are not configured in the runtime environment.
    """
    # 1) Preferred: Streamlit secrets
    try:
        key = st.secrets["ilovepdf"]["public"]
        if isinstance(key, str) and key.strip():
            return key.strip()
    except Exception:
        pass

    # 2) Fallback: project file data/stream.toml (very lightweight parser)
    try:
        base = os.path.dirname(__file__)
        candidate = os.path.join(base, "data", "stream.toml")
        if os.path.exists(candidate):
            in_section = False
            with open(candidate, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("[") and line.endswith("]"):
                        # entering/exiting sections
                        in_section = line.strip("[]").strip() == "ilovepdf"
                        continue
                    if in_section and line.lower().startswith("public") and "=" in line:
                        # parse value between quotes public = "..."
                        try:
                            after_eq = line.split("=", 1)[1].strip()
                            if after_eq.startswith('"') and after_eq.endswith('"'):
                                val = after_eq.strip('"')
                                if val:
                                    return val
                        except Exception:
                            continue
    except Exception:
        pass

    return None


def _get_disable_local_fallback() -> bool:
    """Return whether local fallback should be disabled.

    Checks st.secrets first, then data/stream.toml for a boolean
    `disable_local_fallback` inside the [ilovepdf] section.
    """
    # 1) secrets
    try:
        v = st.secrets["ilovepdf"].get("disable_local_fallback", False)
        if isinstance(v, bool):
            return v
        # accept string-y booleans too
        if isinstance(v, str):
            return v.strip().lower() in {"1", "true", "yes", "on"}
    except Exception:
        pass

    # 2) data/stream.toml
    try:
        base = os.path.dirname(__file__)
        candidate = os.path.join(base, "data", "stream.toml")
        if os.path.exists(candidate):
            in_section = False
            with open(candidate, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("[") and line.endswith("]"):
                        in_section = line.strip("[]").strip() == "ilovepdf"
                        continue
                    if in_section and line.lower().startswith("disable_local_fallback") and "=" in line:
                        try:
                            after_eq = line.split("=", 1)[1].strip().strip('"').strip("'")
                            return after_eq.lower() in {"1", "true", "yes", "on"}
                        except Exception:
                            continue
    except Exception:
        pass

    return False


def _try_local_docx2pdf(docx_bytes: bytes, filename: str) -> Optional[bytes]:
    """Windows-only local DOCX→PDF using docx2pdf. No Linux/macOS fallback."""
    if _get_disable_local_fallback():
        _record_error("Local fallback disabled by configuration.")
        return None
    if platform.system() != "Windows":
        # Explicitly do nothing on non-Windows per requirements
        return None
    try:
        from docx2pdf import convert  # type: ignore
    except Exception:
        _record_error("docx2pdf module not available on Windows.")
        return None
    com_inited = False
    try:
        try:
            import pythoncom  # type: ignore
            pythoncom.CoInitialize()
            com_inited = True
        except Exception as e:
            _record_error(f"COM init failed: {e}")
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
        _record_error(f"docx2pdf error: {e}")
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
    public_key = _get_ilovepdf_public_key()
    if not public_key:
        _record_error("Missing iLovePDF public key. Configure .streamlit/secrets.toml or data/stream.toml.")
        if _get_disable_local_fallback():
            return None
        return _try_local_docx2pdf(docx_bytes, filename)

    # --- iLovePDF remote flow ---
    try:
        # 1. Auth (only public_key needed per API spec)
        auth_resp = requests.post(ILOVEPDF_AUTH_URL, json={"public_key": public_key}, timeout=30)
        if auth_resp.status_code != 200:
            _record_error(f"Auth failed ({auth_resp.status_code}): {auth_resp.text[:120]}")
            if platform.system() == "Windows" and not _get_disable_local_fallback():
                return _try_local_docx2pdf(docx_bytes, filename)
            return None
        token = auth_resp.json().get("token")
        if not token:
            _record_error("Token missing in auth response.")
            if platform.system() == "Windows" and not _get_disable_local_fallback():
                return _try_local_docx2pdf(docx_bytes, filename)
            return None
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Create task
        task_resp = requests.post(ILOVEPDF_CREATE_TASK_URL, json={"tool": "officepdf"}, headers=headers, timeout=30)
        if task_resp.status_code != 200:
            _record_error(f"Create task failed ({task_resp.status_code}): {task_resp.text[:120]}")
            if platform.system() == "Windows" and not _get_disable_local_fallback():
                return _try_local_docx2pdf(docx_bytes, filename)
            return None
        tj = task_resp.json()
        task_id = tj.get("task")
        server = tj.get("server")
        if not task_id or not server:
            _record_error("Task or server missing in create-task response.")
            if platform.system() == "Windows" and not _get_disable_local_fallback():
                return _try_local_docx2pdf(docx_bytes, filename)
            return None

        # 3. Upload (field must be files[] per API docs)
        upload_url = f"https://{server}/v1/upload"
        file_stream = io.BytesIO(docx_bytes)
        files = {"files[]": (f"{filename}.docx", file_stream, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        form_data = {"task": task_id}
        up_resp = requests.post(upload_url, files=files, data=form_data, headers=headers, timeout=120)
        if up_resp.status_code != 200:
            _record_error(f"Upload failed ({up_resp.status_code}): {up_resp.text[:120]}")
            if platform.system() == "Windows" and not _get_disable_local_fallback():
                return _try_local_docx2pdf(docx_bytes, filename)
            return None

        # 4. Process (must include tool)
        process_url = f"https://{server}/v1/process"
        proc_payload = {"task": task_id, "tool": "officepdf"}
        proc_resp = requests.post(process_url, json=proc_payload, headers=headers, timeout=180)
        if proc_resp.status_code != 200:
            _record_error(f"Process failed ({proc_resp.status_code}): {proc_resp.text[:120]}")
            if platform.system() == "Windows" and not _get_disable_local_fallback():
                return _try_local_docx2pdf(docx_bytes, filename)
            return None

        # 5. Download
        download_url = f"https://{server}/v1/download/{task_id}"
        dl_resp = requests.get(download_url, headers=headers, timeout=180)
        if dl_resp.status_code != 200:
            _record_error(f"Download failed ({dl_resp.status_code}): {dl_resp.text[:120]}")
            if platform.system() == "Windows" and not _get_disable_local_fallback():
                return _try_local_docx2pdf(docx_bytes, filename)
            return None

        return dl_resp.content
    except requests.Timeout:
        _record_error("iLovePDF network timeout.")
        if platform.system() == "Windows" and not _get_disable_local_fallback():
            return _try_local_docx2pdf(docx_bytes, filename)
        return None
    except Exception as e:
        _record_error(f"Unexpected iLovePDF error: {e}")
        if platform.system() == "Windows" and not _get_disable_local_fallback():
            return _try_local_docx2pdf(docx_bytes, filename)
        return None


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
