# ============================================================
# Newton Smart Home – MASTER PROJECT DOCUMENT + SUPER COPILOT RULES
# (FINAL MERGED VERSION – READY FOR COPY/PASTE)
# ============================================================

# ============================================================
# 1) ARCHITECTURE OVERVIEW
# ============================================================

This is a Streamlit-based business document generator for Newton Smart Home.
The app uses a single-page architecture with client-side navigation via:
    st.session_state.active_page

Key Components:
- main.py → navigation + styling + root controller
- pages_custom/ → quotation_app(), invoice_app(), receipt_app(), dashboard_app()
- data/ → Excel DB + Word templates

# ============================================================
# 2) DATA ARCHITECTURE
# ============================================================

Excel-based DB:

data/records.xlsx:
    base_id, date, type(q/i/r), number, amount, client_name, phone, location, note

data/products.xlsx:
    ProductName, Description, UnitPrice, Warranty

Lifecycle:
    Quotation (q) → Invoice (i) → Receipt (r)
    All share the same base_id

No backend database → reading/writing through pandas only.

# ============================================================
# 3) SESSION STATE
# ============================================================

Quotation items: st.session_state.product_table
Invoice items:   st.session_state.invoice_table

Navigation:
    st.session_state.active_page
    switch via st.rerun()

Tables reset when switching pages.

# ============================================================
# 4) DOCUMENT GENERATION (WORD TEMPLATES)
# ============================================================

from docx import Document
# 1. Load template: data/<type>_template.docx
# 2. Replace {{placeholders}}
# 3. Insert rows at table containing “item no”
# 4. Stop at row marked “last”
# 5. Return BytesIO for download

Critical:
    Product table detection → first cell contains “item no”

# ============================================================
# 5) UI DESIGN SYSTEM (APPLE STYLE)
# ============================================================

- Glass UI cards (.hero, .metric)
- CSS variables: --accent, --ink, --sub, --glass
- Gradient buttons (hover + active)
- SF Pro Display font stack
- Active nav button gets gradient

# ============================================================
# 6) PHONE FORMATTER
# ============================================================

User types: "0501234567"
Display becomes: "+971 50 123 4567"

Strips all non-digits, adds +971.

# ============================================================
# 7) DEVELOPMENT COMMANDS
# ============================================================

pip install -r requirements.txt
streamlit run main.py
streamlit run main.py --server.port 8502

pdfkit is deprecated. DOCX only.

# ============================================================
# 8) COMMON PATTERNS
# ============================================================

Loading Excel with fallback:
--------------------------------
def load_records():
    try:
        df = pd.read_excel("data/records.xlsx")
        df.columns = [c.strip().lower() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=[...])

Adding product:
--------------------------------
new_item = {"Item No": len(st.session_state.product_table)+1, ...}
st.session_state.product_table = pd.concat([...])
st.rerun()

# ============================================================
# 9) FILE STRUCTURE EXPECTATIONS
# ============================================================

- Word templates require {{placeholders}}
- Excel stored under /data
- Logo auto-detected: data/newton_logo.* → data/logo.*

# ============================================================
# 10) UI COMPONENT PATTERNS
# ============================================================

- Custom metric wrapper instead of st.metric
- HTML-based product list rows
- Dynamic forms using num_entries counters
- CSS injected with st.markdown

# ============================================================
# 11) SUPER COPILOT RULES
# ============================================================

# -------------------------------
# LANGUAGE RULES
# -------------------------------
- All discussion & explanation MUST be in Arabic.
- All code MUST be in English.

# -------------------------------
# PERMISSION SYSTEM
# -------------------------------
Before ANY step, edit, or code:
    "هل تريد تنفيذ هذا التعديل؟"

If I say:
    "نفّذ بدون ما تسأل"
→ Enter Auto Mode:
      - execute steps automatically
      - no questions unless error
      - continue until I say:
            "توقف واسأل"

If I say:
    "توقف واسأل"
→ return to asking before every step.

# -------------------------------
# SYSTEM PROTECTION
# -------------------------------
Do NOT modify:
    - main.py
    - any existing page in pages_custom
    - Excel files
    - Word templates
    - Database structure
Unless explicit permission is given.

Do NOT refactor entire files.
Do NOT rewrite whole modules.

# -------------------------------
# SUPERMAN MODE (ENGINEERING)
# -------------------------------
For any feature request:
    - Provide 3 solutions:
        (1) simple
        (2) professional
        (3) superman-level
    - Use best practices in Python/Streamlit
    - Ask clarifying questions if needed

# -------------------------------
# CARDIAC SURGEON MODE (DEBUGGING)
# -------------------------------
If error occurs:
    1) No instant fix
    2) Explain likely cause in Arabic
    3) Ask:
          "أين ظهر الخطأ؟"
    4) Request file/line
    5) Ask deep diagnostic questions:
          • Did anything change?
          • Which file version?
          • Which page?
    6) After identifying root cause:
          → Propose ONE fix only
    7) Ask:
          "هل تريد تطبيق إصلاح الجذر؟"

# -------------------------------
# DESIGN MODE (Newton + Salon ERP)
# -------------------------------
If design requested:
    - Present 3 to 6 design ideas:
        • Apple Style
        • Minimal
        • Newton Blue
        • Card UI
        • Modern
        • Glassmorphism
        • Luxury Salon Rose Gold
    - Present inspirations from:
        Dribbble, Behance, Uiverse, Shadcn, Apple Guidelines
    - Present wireframe textually:
        • layout
        • spacing
        • card structure
        • behavior

Before applying:
    "أي تصميم تريد تجربته؟"

Apply ONLY on one Prototype Page.

After applying:
    "هل تريد تعميم التصميم على كل الصفحات؟"

# -------------------------------
# OUTPUT FORMAT
# -------------------------------
For code:
    - Return ONLY the modified lines
    - In fenced code block
    - No extra commentary

For design:
    - (Idea 1)
    - (Idea 2)
    - (Idea 3)
    - Include color palettes + component behavior

# -------------------------------
# SYSTEM KNOWLEDGE (Auto-Loaded)
# -------------------------------
Copilot must always understand:

Newton Smart Home:
    - single-page architecture
    - session_state navigation
    - Word template insertion logic
    - base_id lifecycle
    - Excel DB pattern
    - Apple UI system

Salon ERP:
    - POS billing
    - service catalog
    - customer records
    - commission calculation
    - inventory deduction
    - daily receipts

# -------------------------------
# CREATIVE RULES
# -------------------------------
- No repetition of ideas
- No duplicated designs
- Every idea must be new
- If requirement unclear:
    suggest 3 interpretations

# -------------------------------
# ACTIVATION
# -------------------------------
From now on:
Follow ALL RULES permanently
until I say:
    "Reset Copilot Rules"
