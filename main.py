import streamlit as st
import os
from base64 import b64encode
from pages_custom.quotation_page import quotation_app
from pages_custom.invoice_page import invoice_app
from pages_custom.receipt_page import receipt_app
from pages_custom.dashboard_page import dashboard_app
from pages_custom.customers_page import customers_app
from pages_custom.products_page import products_app

st.set_page_config(page_title="Newton Smart Home OS", layout="wide")

# Load logo as data URI
def _load_logo_datauri():
    candidates = ["data/newton_logo.png", "data/newton_logo.svg", "data/logo.png", "data/logo.svg"]
    base = os.path.dirname(__file__)
    for rel in candidates:
        path = os.path.join(base, rel)
        if os.path.exists(path):
            ext = os.path.splitext(path)[1].lower()
            mime = "image/png" if ext == ".png" else "image/svg+xml" if ext == ".svg" else None
            if not mime:
                continue
            with open(path, "rb") as f:
                data = b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{data}"
    return None

st.markdown(
    """
    <style>
    :root { 
        --brand-blue:#0a84ff; /* kept for nav highlights */
        --accent:#0a84ff; --accent-light:#5ac8fa; 
        --ink:#1d1d1f; --sub:#6e6e73; 
        --glass:rgba(255,255,255,.95); --glass-border:rgba(0,0,0,.06);
        --text-primary:#1d1d1f;
    }
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(180deg,#fafafa 0%,#f0f0f5 100%);
        font-family: "SF Pro Display", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text-primary);
    }
    [data-testid="stHeader"] { background-color: transparent; }

    .hero-card{
        background: linear-gradient(135deg, rgba(255,255,255,.95) 0%, rgba(248,248,252,.92) 100%);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 28px 32px;
        box-shadow: 0 2px 8px rgba(0,0,0,.04), 0 12px 32px rgba(0,0,0,.08);
        backdrop-filter: blur(20px);
        margin-bottom: 18px;
    }

    /* New header layout: left (page title) | center (nav buttons) | right (logo) */
    .header-container{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 24px;
        margin-bottom: 12px;
    }
    
    .page-title-section{
        flex: 0 0 auto;
        min-width: 200px;
    }
    
    .page-title{
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin: 0;
        line-height: 1.2;
    }
    
    .page-subtitle{
        font-size: 14px;
        color: #6e6e73;
        margin: 4px 0 0 0;
    }
    
    .nav-buttons-section{
        flex: 1;
        display: flex;
        justify-content: center;
        gap: 12px;
    }
    
    .logo-section{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        min-width: 200px;
    }
    
    .logo-badge{
        width: 120px;
        height: auto;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,.12);
    }

    /* Compact vertical rhythm */
    [data-testid="block-container"]{ padding-top: 4px !important; }
    div[data-testid="element-container"]{ margin-bottom: 6px !important; }
    [data-testid="stButton"]{ margin-bottom: 0 !important; }

    /* Nav buttons - adjusted for horizontal layout */
    [data-testid="stButton"] > button{
        border: none !important;
        border-radius: 20px !important;
        padding: 14px 20px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        background: linear-gradient(145deg, #ffffff 0%, #f9f9fb 100%) !important;
        color: var(--ink) !important;
        box-shadow: 0 8px 20px rgba(15,23,42,.12) !important;
        transition: transform .18s, box-shadow .18s !important;
        white-space: nowrap !important;
    }
    [data-testid="stButton"] > button:hover{
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 28px rgba(15,23,42,.18) !important;
    }

    /* Uniform sizing for top nav buttons (4 cards) */
    button[key^="nav_"]{
        min-height: 48px !important;
        height: 48px !important;
        padding: 10px 16px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 16px !important;
        white-space: nowrap !important;
        font-size: 0.93rem !important;
        line-height: 1 !important;
    }
    /* Sidebar items consistent height as well */
    button[key^="sidenav_"]{
        min-height: 44px !important;
        height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border-radius: 12px !important;
        font-size: 0.93rem !important;
    }

    /* Global form controls to match Invoice theme across all pages */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] select{
        background:#fff!important;
        border:1px solid rgba(0,0,0,.08)!important;
        border-radius:12px!important;
        padding:10px 14px!important;
        font-size:14px!important;
        color:var(--text-primary)!important;
        box-shadow:0 2px 6px rgba(0,0,0,.04)!important;
        height:40px!important;
        outline:none!important;
        transition: border-color .12s ease, box-shadow .12s ease !important;
    }
    [data-testid="stTextInput"] input:focus,
    [data-testid="stNumberInput"] input:focus,
    [data-testid="stSelectbox"] select:focus{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px rgba(10,132,255,.12) !important;
    }
    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stNumberInput"] input::placeholder{
        color: #9ca3af !important;
        opacity: 1 !important;
    }
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[role="combobox"],
    .stSelectbox div[role="listbox"],
    .stSelectbox [role="option"]{
        background:#fff !important;
        color: var(--text-primary) !important;
    }
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[role="combobox"] > div{
        background:#fff !important;
    }
    .stSelectbox div[data-baseweb="select"]:focus-within,
    .stSelectbox div[role="combobox"]:focus-within{
        background:#fff !important;
    }
    .stSelectbox svg{ color: var(--text-primary) !important; }
    .stSelectbox [role="option"][aria-selected="true"]{
        background:#f3f4f6 !important;
        color: var(--text-primary) !important;
    }

    /* Common utility classes from Invoice theme */
    .section-title{ font-size:20px; font-weight:700; margin:18px 0 10px; color:var(--ink); }
    .added-product-row{
        background:#ffffff; padding:10px 14px; border:1px solid rgba(0,0,0,.08);
        border-radius:12px; margin-bottom:6px; box-shadow:0 2px 6px rgba(0,0,0,.05);
    }
    .product-header{
        display:flex; gap:1rem; padding:8px 0 12px;
        border-bottom:1px solid rgba(0,0,0,.08); background:transparent;
        font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:#86868b;
        margin-bottom:10px; align-items:center;
    }
    .product-header span{text-align:center;}
    .product-header span:nth-child(1){flex:4.5; text-align:left;}
    .product-header span:nth-child(2){flex:0.7;}
    .product-header span:nth-child(3){flex:1;}
    .product-header span:nth-child(4){flex:1;}
    .product-header span:nth-child(5){flex:0.7;}
    .product-header span:nth-child(6){flex:0.7;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "active_page" not in st.session_state:
    st.session_state.active_page = "dashboard"

# Page titles mapping
PAGE_TITLES = {
    "dashboard": ("Newton Dashboard", "Monitor live analytics"),
    "quotation": ("Newton Quotation", "Draft elegant proposals"),
    "invoice": ("Newton Invoice", "Bill with confidence"),
    "receipt": ("Newton Receipt", "Acknowledge payments"),
    "customers": ("Customers", "Manage client accounts"),
    "products": ("Products", "Manage catalog"),
    "reports": ("Reports", "Business insights"),
    "settings": ("Settings", "Configure application"),
}

# Load logo
_logo_uri = _load_logo_datauri()
_logo_html = f'<img src="{_logo_uri}" alt="Newton Smart Home" class="logo-badge" />' if _logo_uri else '<div style="width:120px;height:80px;background:linear-gradient(135deg,#0a84ff,#5bc0ff);border-radius:16px;display:flex;align-items:center;justify-content:center;color:white;font-weight:700;font-size:18px;">NEWTON</div>'

# Get current page info
current_title, current_subtitle = PAGE_TITLES.get(st.session_state.active_page, ("Dashboard", "Monitor live analytics"))

# Header structure
st.markdown(
    f"""
    <div class="hero-card">
        <div class="header-container">
            <div class="page-title-section">
                <h1 class="page-title">{current_title}</h1>
                <p class="page-subtitle">{current_subtitle}</p>
            </div>
            <div class="nav-buttons-section" id="nav-buttons-placeholder"></div>
            <div class="logo-section">
                {_logo_html}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar navigation (mirrors top nav)
with st.sidebar:
    st.markdown("<div style='font-weight:700;margin-bottom:6px;color:#0f172a;'>Navigation</div>", unsafe_allow_html=True)
    _side_nav_items = [
        ("dashboard", "⌁ Dashboard"),
        ("quotation", "✦ Quotation"),
        ("invoice", "◉ Invoice"),
        ("receipt", "⬡ Receipt"),
        ("customers", "Customers"),
        ("products", "Products"),
        ("reports", "Reports"),
        ("settings", "Settings"),
    ]
    for page_id, title in _side_nav_items:
        if st.button(title, key=f"sidenav_{page_id}", use_container_width=True):
            st.session_state.active_page = page_id
            st.rerun()

    # Highlight active in sidebar
    st.markdown(
        f"""
        <style>
        button[key=\"sidenav_{st.session_state.active_page}\"] {{
            background: linear-gradient(140deg, var(--brand-blue), #5bc0ff) !important;
            color: #fff !important;
            box-shadow: 0 18px 32px rgba(10,132,255,0.30) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Navigation buttons (will appear in the center)
NAV_ITEMS = [
    ("dashboard", "⌁ Dashboard"),
    ("quotation", "✦ Quotation"),
    ("invoice", "◉ Invoice"),
    ("receipt", "⬡ Receipt"),
]

nav_cols = st.columns(4)
for col, (page_id, title) in zip(nav_cols, NAV_ITEMS):
    with col:
        pressed = st.button(title, key=f"nav_{page_id}", use_container_width=True)
        if pressed:
            st.session_state.active_page = page_id
            st.rerun()

st.markdown(
    f"""
    <style>
    button[key="nav_{st.session_state.active_page}"] {{
        background: linear-gradient(140deg, var(--brand-blue), #5bc0ff) !important;
        color: #fff !important;
        box-shadow: 0 30px 55px rgba(10,132,255,0.4) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state.active_page == "quotation":
    quotation_app()
elif st.session_state.active_page == "invoice":
    invoice_app()
elif st.session_state.active_page == "receipt":
    receipt_app()
elif st.session_state.active_page == "customers":
    customers_app()
elif st.session_state.active_page == "products":
    products_app()
elif st.session_state.active_page == "reports":
    st.markdown("""
        <div class="hero-card">
            <h3 style="margin:0">Reports</h3>
            <p style="margin:6px 0 0;color:#6e6e73">Coming soon: insights and analytics.</p>
        </div>
    """, unsafe_allow_html=True)
elif st.session_state.active_page == "settings":
    st.markdown("""
        <div class="hero-card">
            <h3 style="margin:0">Settings</h3>
            <p style="margin:6px 0 0;color:#6e6e73">Coming soon: application configuration.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    dashboard_app()
