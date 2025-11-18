# Newton Smart Home - Quotation App

## Architecture Overview

This is a **Streamlit-based business document generator** for Newton Smart Home. The app uses a single-page architecture with client-side navigation via `st.session_state.active_page` instead of Streamlit's native multi-page approach.

**Key Components:**
- `main.py`: Main entry point with navigation system and global styling
- `pages_custom/`: Module-based page functions (`quotation_app()`, `invoice_app()`, `receipt_app()`, `dashboard_app()`)
- `data/`: Excel database files (`records.xlsx`, `products.xlsx`) and Word templates

## Data Architecture

**Excel-based Database Pattern:**
- `data/records.xlsx`: Central transaction log with columns: `base_id`, `date`, `type` (q/i/r), `number`, `amount`, `client_name`, `phone`, `location`, `note`
- `data/products.xlsx`: Product catalog with columns: `ProductName`, `Description`, `UnitPrice`, `Warranty`
- **No backend database** - all persistence through direct Excel file read/write using `pandas`

**Record Lifecycle:**
1. Quotation (type='q') → Invoice (type='i') → Receipt (type='r')
2. All share same `base_id` for tracking relationship
3. Invoice references quotation number; receipt references invoice number

## Streamlit Session State Conventions

**Page-specific tables:**
- `st.session_state.product_table`: Quotation line items (DataFrame)
- `st.session_state.invoice_table`: Invoice line items (DataFrame)
- Reset required when switching pages - tables are NOT global

**Navigation:**
- `st.session_state.active_page`: Current page ("dashboard", "quotation", "invoice", "receipt")
- Navigation through button clicks triggers `st.rerun()` for page switch

## Document Generation Pattern

**All pages use Word template replacement:**
```python
from docx import Document
# 1. Load template from data/<type>_template.docx
# 2. Replace {{placeholders}} in all table cells
# 3. Dynamically insert product rows into specific table (identified by "item no" in first row)
# 4. Delete unused template rows (marked with "last" keyword)
# 5. Return BytesIO for download button
```

**Critical**: Product table detection relies on first cell containing "item no" (case-insensitive). The "last" row marker indicates where to stop inserting products.

## Styling System

**Apple-inspired design system** with CSS-in-Python via `st.markdown()`:
- Glass morphism cards (`.hero`, `.metric`)
- CSS custom properties: `--accent`, `--ink`, `--sub`, `--glass`
- Each page module has its own `_apply_*_theme()` function
- Consistent button styling with hover/active states using gradients
- Font: "SF Pro Display" fallback chain

**Navigation styling**: Active page button gets blue gradient via injected CSS targeting `button[key="nav_{page}"]`.

## Phone Number Formatting

Quotation page implements `format_phone_input()` that auto-formats as user types:
- Input: "0501234567" → Display: "+971 50 123 4567"
- Strips all non-digits, adds +971 country code
- Used for `client_phone` field

## Development Commands

```powershell
# Install dependencies
pip install -r requirements.txt

# Run app (default port 8501)
streamlit run main.py

# Run on custom port
streamlit run main.py --server.port 8502
```

**Note**: `pdfkit` in requirements.txt is legacy - all document generation now uses Word format only.

## Common Patterns

**Loading Excel with fallback:**
```python
def load_records():
    try:
        df = pd.read_excel("data/records.xlsx")
        df.columns = [c.strip().lower() for c in df.columns]  # Normalize columns
        return df
    except:
        return pd.DataFrame(columns=["base_id", "date", "type", ...])
```

**Adding products to session state table:**
```python
new_item = {"Item No": len(st.session_state.product_table) + 1, ...}
st.session_state.product_table = pd.concat([st.session_state.product_table, pd.DataFrame([new_item])], ignore_index=True)
st.rerun()  # Force UI refresh
```

## File Structure Expectations

- Word templates MUST contain `{{placeholder}}` for text replacement
- Excel files must be in `data/` directory (relative paths hardcoded)
- Logo files: app searches `data/newton_logo.{png,svg}` then `data/logo.{png,svg}`

## UI Component Patterns

**Metrics use custom wrapper** (`_metric()` in dashboard) instead of raw `st.metric()` for consistent glass-card styling.

**Product lists** rendered as custom HTML using `.added-product-row` class instead of Streamlit dataframes for better visual control.

**Dynamic forms**: Use `st.session_state.num_entries` counter pattern for multiple product input rows in single form.

and always answer to me with arabic language 
