import os
from base64 import b64encode

import streamlit as st

from pages_custom.quotation_page import quotation_app
from pages_custom.invoice_page import invoice_app
from pages_custom.receipt_page import receipt_app
from pages_custom.customers_page import customers_app
from pages_custom.products_page import products_app
from pages_custom.reports_page import reports_app
from pages_custom.settings_page import settings_app
from pages_custom.dashboard_page import dashboard_app
from utils.auth import validate_pin, can_access_page, is_admin
from utils.logger import log_event


# ===========================
# THEME ENGINE (Newton Mint)
# ===========================
if "ui_theme" not in st.session_state:
    # Start in dark Newton mode by default
    st.session_state.ui_theme = "dark"

# --- LIGHT THEME (Newton Mint Light) ---
light_css = """
<style>
:root {
    --newton-mint: #00FFC6;
    --newton-glow: rgba(0,255,198,0.25);
    --newton-carbon: #0D0F11;
    --newton-graphite: #161A1E;
    --newton-white: #F4F7FA;
    --newton-grey: #AEB5BE;

    --bg-primary: #F4F7FA;
    --bg-card: #FFFFFF;
    --bg-input: #FFFFFF;
    --bg-sidebar: #FFFFFF;

    --text: #0D0F11;
    --text-soft: #6E6E73;

    --border: rgba(15,23,42,0.12);
    --border-soft: rgba(15,23,42,0.06);

    --button: #00FFC6;
    --button-hover: rgba(0,255,198,0.9);

    --accent: #00FFC6;
}

/* App shell */
[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(circle at top left, rgba(0,255,198,0.08), transparent 55%),
        radial-gradient(circle at bottom right, rgba(0,255,198,0.06), transparent 55%),
        var(--bg-primary) !important;
    color: var(--text) !important;
    font-family: "Inter","Poppins",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif !important;
}
[data-testid="stHeader"]{ background: transparent !important; }

[data-testid="stSidebar"]{
    background: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border-soft);
    box-shadow: 0 0 18px rgba(15,23,42,0.12);
}

/* Layout */
[data-testid="block-container"]{
    padding-top: 10px !important;
}
div[data-testid="element-container"]{
    margin-bottom: 8px !important;
}

/* Hero header */
.hero-card{
    background: linear-gradient(135deg,#FFFFFF 0%,#F4F7FA 100%) !important;
    border-radius: 24px !important;
    border: 1px solid var(--border-soft) !important;
    box-shadow: 0 20px 45px rgba(15,23,42,0.12) !important;
    padding: 24px 28px !important;
    overflow: visible;
    position: relative;
}
.header-container{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:24px;
    min-height:80px;
}
.page-title-section{
    flex:0 0 auto;
    min-width:200px;
}
.nav-buttons-section{
    flex:1;
    display:flex;
    justify-content:center;
    gap:12px;
}
.logo-section{
    flex:0 0 auto;
    display:flex;
    align-items:center;
    justify-content:flex-end;
    min-width:200px;
}
.logo-badge{
    max-height:72px;
    width:auto;
}
.page-title{
    font-size: 28px;
    font-weight: 700;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--text);
    margin: 0;
}
.page-subtitle{
    font-size: 13px;
    color: var(--text-soft);
    margin-top: 6px;
}
.mint-underline{
    margin-top: 10px;
    width: 140px;
    height: 2px;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--accent), transparent);
    box-shadow: 0 0 18px var(--newton-glow);
}

/* Buttons */
button[key^="nav_"],
button[key^="sidenav_"],
[data-testid="stButton"] > button{
    background: var(--bg-card) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 4px 10px rgba(15,23,42,0.08) !important;
    padding: 8px 14px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    transition: all .18s ease-out !important;
    white-space: nowrap !important;
}
button[key^="nav_"]:hover,
button[key^="sidenav_"]:hover,
[data-testid="stButton"] > button:hover{
    box-shadow: 0 8px 18px rgba(15,23,42,0.18) !important;
    transform: translateY(-1px) !important;
    border-color: var(--accent) !important;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select,
textarea{
    background: var(--bg-input) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder{
    color: var(--text-soft) !important;
}

/* BaseWeb Select */
.stSelectbox div[data-baseweb="select"],
.stSelectbox div[role="combobox"]{
    background: var(--bg-input) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="popover"]{
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border-soft) !important;
    z-index: 9999 !important;
}
[data-baseweb="menu"] li,
[data-baseweb="menu-item"]{
    background: var(--bg-card) !important;
    color: var(--text) !important;
}
[data-baseweb="menu-item"]:hover{
    background: rgba(0,255,198,0.12) !important;
}

/* Tables */
[data-testid="stTable"] table{
    background: var(--bg-card) !important;
    color: var(--text) !important;
}
[data-testid="stTable"] th{
    color: var(--text-soft) !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTable"] td{
    color: var(--text) !important;
    border-bottom: 1px solid var(--border-soft) !important;
}
</style>
"""

# --- DARK THEME (Newton Mint Dark Futuristic) ---
dark_css = """
<style>
:root {
    --newton-mint: #00FFC6;
    --newton-glow: rgba(0,255,198,0.25);
    --newton-carbon: #0D0F11;
    --newton-graphite: #161A1E;
    --newton-white: #F4F7FA;
    --newton-grey: #AEB5BE;

    --bg-primary: #0D0F11;
    --bg-card: #161A1E;
    --bg-input: #181C21;
    --bg-sidebar: #0D0F11;

    --text: #F4F7FA;
    --text-soft: #AEB5BE;

    --border: rgba(0,255,198,0.30);
    --border-soft: rgba(0,255,198,0.16);

    --button: #00FFC6;
    --button-hover: rgba(0,255,198,0.9);

    --accent: #00FFC6;
}

/* App shell */
[data-testid="stAppViewContainer"]{
    background:
        radial-gradient(circle at top left, rgba(0,255,198,0.15), transparent 55%),
        radial-gradient(circle at bottom right, rgba(0,255,198,0.12), transparent 55%),
        var(--bg-primary) !important;
    color: var(--text) !important;
    font-family: "Inter","Poppins",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif !important;
}
[data-testid="stHeader"]{ background: transparent !important; }

[data-testid="stSidebar"]{
    background: var(--bg-sidebar) !important;
    border-right: 1px solid rgba(0,255,198,0.35);
    box-shadow: 0 0 28px rgba(0,0,0,0.8);
}

/* Layout */
[data-testid="block-container"]{
    padding-top: 10px !important;
}
div[data-testid="element-container"]{
    margin-bottom: 8px !important;
}

/* Hero header */
.hero-card{
    background:
        radial-gradient(circle at top left, rgba(0,255,198,0.10), transparent 55%),
        radial-gradient(circle at bottom right, rgba(0,255,198,0.10), transparent 55%),
        #111318 !important;
    border-radius: 24px !important;
    border: 1px solid rgba(0,255,198,0.30) !important;
    box-shadow: 0 0 30px rgba(0,255,198,0.25) !important;
    padding: 24px 28px !important;
    overflow: visible;
    position: relative;
}
.header-container{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:24px;
    min-height:80px;
}
.page-title-section{
    flex:0 0 auto;
    min-width:200px;
}
.nav-buttons-section{
    flex:1;
    display:flex;
    justify-content:center;
    gap:12px;
}
.logo-section{
    flex:0 0 auto;
    display:flex;
    align-items:center;
    justify-content:flex-end;
    min-width:200px;
}
.logo-badge{
    max-height:72px;
    width:auto;
}
.page-title{
    font-size: 28px;
    font-weight: 700;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--text);
    margin: 0;
}
.page-subtitle{
    font-size: 13px;
    color: var(--text-soft);
    margin-top: 6px;
}
.mint-underline{
    margin-top: 10px;
    width: 160px;
    height: 2px;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--accent), transparent);
    box-shadow: 0 0 20px var(--newton-glow);
}

/* Buttons */
button[key^="nav_"],
button[key^="sidenav_"],
[data-testid="stButton"] > button{
    background: var(--bg-card) !important;
    color: var(--text) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(0,255,198,0.22) !important;
    box-shadow: 0 0 18px rgba(0,255,198,0.18) !important;
    padding: 8px 14px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    transition: all .18s ease-out !important;
    white-space: nowrap !important;
}
button[key^="nav_"]:hover,
button[key^="sidenav_"]:hover,
[data-testid="stButton"] > button:hover{
    box-shadow: 0 0 26px rgba(0,255,198,0.35) !important;
    transform: translateY(-1px) !important;
    border-color: var(--accent) !important;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] select,
textarea{
    background: var(--bg-input) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stTextInput"] input::placeholder,
[data-testid="stNumberInput"] input::placeholder{
    color: var(--text-soft) !important;
}

/* BaseWeb Select */
.stSelectbox div[data-baseweb="select"],
.stSelectbox div[role="combobox"]{
    background: var(--bg-input) !important;
    color: var(--text) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border) !important;
}
[data-baseweb="popover"]{
    background: var(--bg-card) !important;
    border-radius: 12px !important;
    border: 1px solid var(--border-soft) !important;
    z-index: 9999 !important;
}
[data-baseweb="menu"] li,
[data-baseweb="menu-item"]{
    background: var(--bg-card) !important;
    color: var(--text) !important;
}
[data-baseweb="menu-item"]:hover{
    background: rgba(0,255,198,0.12) !important;
}

/* Tables */
[data-testid="stTable"] table{
    background: var(--bg-card) !important;
    color: var(--text) !important;
}
[data-testid="stTable"] th{
    color: var(--text-soft) !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stTable"] td{
    color: var(--text) !important;
    border-bottom: 1px solid var(--border-soft) !important;
}
</style>
"""


def inject_theme() -> None:
    """Inject current theme CSS (Newton light/dark)."""
    if st.session_state.ui_theme == "light":
        st.markdown(light_css, unsafe_allow_html=True)
    else:
        st.markdown(dark_css, unsafe_allow_html=True)


# Must be first Streamlit call
st.set_page_config(page_title="Newton Smart Home OS", layout="wide")
inject_theme()


# ===========================
# PIN LOGIN SYSTEM
# ===========================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "show_pin" not in st.session_state:
    st.session_state.show_pin = False

if not st.session_state.authenticated:
    st.markdown(
        """
        <div style='text-align:center; padding:60px 20px;'>
            <h1 style='color:var(--accent); font-size:48px; margin-bottom:10px; letter-spacing:.18em; text-transform:uppercase;'>
                Secure Access
            </h1>
            <h2 style='color:var(--text);'>Newton Smart Home</h2>
            <p style='color:var(--text-soft);'>Enter your PIN to continue</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 2, 1])
    with col:
        pin_input = st.text_input(
            "PIN",
            type="password" if not st.session_state.show_pin else "default",
            max_chars=6,
            placeholder="Enter 4-6 digit PIN",
            label_visibility="collapsed",
        )

        show_hide = st.checkbox(
            "Show PIN", value=st.session_state.show_pin, key="show_pin_checkbox"
        )
        if show_hide != st.session_state.show_pin:
            st.session_state.show_pin = show_hide
            st.rerun()

        if st.button("Login", use_container_width=True):
            user_data = validate_pin(pin_input)
            if user_data:
                st.session_state.authenticated = True
                st.session_state.user = user_data
                log_event(
                    user_data["name"],
                    "Login",
                    "login_success",
                    f"Role: {user_data['role']}",
                )
                st.success(f"✅ Welcome, {user_data['name']}!")
                st.rerun()
            else:
                log_event(
                    "Unknown",
                    "Login",
                    "login_failed",
                    f"Invalid PIN: {pin_input[:2]}***",
                )
                st.error("❌ Invalid PIN. Please try again.")

        st.markdown(
            "<div style='text-align:center; margin-top:40px; color:var(--text-soft); font-size:12px;'>"
            "Default PINs: Admin=1234, Staff=5678, Viewer=9999"
            "</div>",
            unsafe_allow_html=True,
        )

    st.stop()


# ===========================
# GLOBAL STRUCTURE
# ===========================
def _load_logo_datauri() -> str | None:
    candidates = [
        "data/newton_logo.png",
        "data/newton_logo.svg",
        "data/logo.png",
        "data/logo.svg",
    ]
    base = os.path.dirname(__file__)
    for rel in candidates:
        path = os.path.join(base, rel)
        if os.path.exists(path):
            ext = os.path.splitext(path)[1].lower()
            mime = (
                "image/png"
                if ext == ".png"
                else "image/svg+xml" if ext == ".svg" else None
            )
            if not mime:
                continue
            with open(path, "rb") as f:
                data = b64encode(f.read()).decode("utf-8")
            return f"data:{mime};base64,{data}"
    return None


if "active_page" not in st.session_state:
    st.session_state.active_page = "dashboard"

PAGE_TITLES = {
    "dashboard": ("Executive Dashboard", "Real-time AI insights for Newton Smart Home"),
    "quotation": ("Newton Quotation", "Draft elegant proposals"),
    "invoice": ("Newton Invoice", "Bill with confidence"),
    "receipt": ("Newton Receipt", "Acknowledge payments"),
    "customers": ("Customers", "Manage client accounts"),
    "products": ("Products", "Manage catalog"),
    "reports": ("Reports", "Business insights"),
    "settings": ("Settings", "Configure application"),
}

ICON_MAP = {
    "dashboard": "📊",
    "quotation": "📝",
    "invoice": "💳",
    "receipt": "🧾",
    "customers": "👥",
    "products": "📦",
    "reports": "📈",
    "settings": "⚙️",
    "logout": "🚪",
    "dark": "🌙",
    "light": "☀️",
}

_logo_uri = _load_logo_datauri()
_logo_html = (
    f'<img src="{_logo_uri}" alt="Newton Smart Home" class="logo-badge" />'
    if _logo_uri
    else '<div style="width:140px;height:64px;background:linear-gradient(135deg,#00FFC6,#18A5A5);'
    "border-radius:18px;display:flex;align-items:center;justify-content:center;"
    'color:#0D0F11;font-weight:700;font-size:18px;">NEWTON</div>'
)

current_title, current_subtitle = PAGE_TITLES.get(
    st.session_state.active_page, ("Executive Dashboard", "Real-time insights")
)

# ---------------------------
# HERO HEADER
# ---------------------------
st.markdown(
    f"""
    <div class="hero-card">
        <div class="header-container">
            <div class="page-title-section">
                <h1 class="page-title">{current_title}</h1>
                <p class="page-subtitle">{current_subtitle}</p>
                <div class="mint-underline"></div>
            </div>
            <div class="nav-buttons-section"></div>
            <div class="logo-section">
                {_logo_html}
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# SIDEBAR
# ---------------------------
with st.sidebar:
    user = st.session_state.get("user") or {}
    user_name = user.get("name", "User")
    user_role = user.get("role", "viewer")

    st.markdown(
        f"""
        <div style='padding:12px; background:var(--bg-card); border-radius:12px;
                    margin-bottom:16px; border:1px solid var(--border-soft);'>
            <div style='font-weight:600; color:var(--text);'>User: {user_name}</div>
            <div style='font-size:12px; color:var(--text-soft); margin-top:4px;'>
                Role: {user_role.title()}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        f"{ICON_MAP['logout']} Logout", use_container_width=True, key="logout_btn"
    ):
        log_event(user_name, "System", "logout", "User logged out")
        st.session_state.authenticated = False
        st.session_state.user = None
        st.rerun()

    st.markdown("---")

    # Theme toggle
    if st.session_state.ui_theme == "light":
        if st.button(f"{ICON_MAP['dark']} Dark Mode", key="toggle_dark"):
            st.session_state.ui_theme = "dark"
            st.rerun()
    else:
        if st.button(f"{ICON_MAP['light']} Light Mode", key="toggle_light"):
            st.session_state.ui_theme = "light"
            st.rerun()

    st.markdown(
        "<div style='font-weight:700;margin:6px 0;color:var(--text-soft);'>Navigation</div>",
        unsafe_allow_html=True,
    )

    side_nav_items = [
        ("dashboard", f"{ICON_MAP['dashboard']} Dashboard"),
        ("quotation", f"{ICON_MAP['quotation']} Quotation"),
        ("invoice", f"{ICON_MAP['invoice']} Invoice"),
        ("receipt", f"{ICON_MAP['receipt']} Receipt"),
        ("customers", f"{ICON_MAP['customers']} Customers"),
        ("products", f"{ICON_MAP['products']} Products"),
        ("reports", f"{ICON_MAP['reports']} Reports"),
        ("settings", f"{ICON_MAP['settings']} Settings"),
    ]

    for page_id, title in side_nav_items:
        if not can_access_page(user, page_id):
            st.markdown(
                f"<div style='padding:8px; color:var(--text-soft); opacity:0.5;'>{title} (Locked)</div>",
                unsafe_allow_html=True,
            )
        else:
            if st.button(title, key=f"sidenav_{page_id}", use_container_width=True):
                st.session_state.active_page = page_id
                st.rerun()

# ---------------------------
# TOP NAV BUTTONS
# ---------------------------
NAV_ITEMS = [
    ("dashboard", f"{ICON_MAP['dashboard']} Dashboard"),
    ("quotation", f"{ICON_MAP['quotation']} Quotation"),
    ("invoice", f"{ICON_MAP['invoice']} Invoice"),
    ("receipt", f"{ICON_MAP['receipt']} Receipt"),
]

nav_cols = st.columns(len(NAV_ITEMS))
for col, (page_id, title) in zip(nav_cols, NAV_ITEMS):
    with col:
        pressed = st.button(title, key=f"nav_{page_id}", use_container_width=True)
        if pressed:
            st.session_state.active_page = page_id
            st.rerun()

# highlight active nav button
st.markdown(
    f"""
    <style>
    button[key="nav_{st.session_state.active_page}"] {{
        background: var(--accent) !important;
        color: #0D0F11 !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ===========================
# PAGE ACCESS CONTROL
# ===========================
current_page = st.session_state.active_page
user = st.session_state.get("user") or {}

if not can_access_page(user, current_page):
    log_event(
        user.get("name", "Unknown"),
        current_page,
        "access_denied",
        f"Attempted to access {current_page}",
    )
    st.error("Access Denied")
    st.warning(
        f"You don't have permission to access the **{current_page.title()}** page."
    )
    st.info(f"Your role: **{user.get('role', 'unknown').title()}**")
    st.markdown("Please contact an administrator if you need access to this page.")
    st.stop()

log_event(
    user.get("name", "Unknown"),
    current_page,
    "access_granted",
    f"Opened {current_page} page",
)

# ===========================
# ROUTING
# ===========================
if current_page == "dashboard":
    dashboard_app()
elif current_page == "quotation":
    quotation_app()
elif current_page == "invoice":
    invoice_app()
elif current_page == "receipt":
    receipt_app()
elif current_page == "customers":
    customers_app()
elif current_page == "products":
    products_app()
elif current_page == "reports":
    reports_app()
elif current_page == "settings":
    settings_app()


_ORBIT_CSS = """
<style>
.orbit-header-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(90deg, #00FFC6 0%, #161A1E 100%);
  border-radius: 18px;
  padding: 0.7rem 1.2rem 0.6rem 1.2rem;
  margin-bottom: 18px;
  box-shadow: 0 2px 18px rgba(0,255,198,0.10);
  border: 1px solid rgba(0,255,198,0.13);
}
.orbit-header-left-label {
  font-size: 0.78rem;
  color: #00FFC6;
  font-weight: 600;
  letter-spacing: .13em;
  text-transform: uppercase;
  margin-bottom: 2px;
}
.orbit-header-main {
  font-size: 1.25rem;
  font-weight: 700;
  color: #F4F7FA;
  letter-spacing: .04em;
}
.orbit-header-right-meta {
  font-size: 0.93rem;
  color: #AEB5BE;
  font-weight: 500;
  letter-spacing: .08em;
  text-align: right;
}
</style>
"""


def _render_exec_header() -> None:
    """Ultra-short header row."""

    # 1) inject ORBITAL MATRIX CSS
    st.markdown(_ORBIT_CSS, unsafe_allow_html=True)

    # 2) render HTML with NO leading spaces (avoid markdown code block)
    st.markdown(
        """
<div class="orbit-header-strip">
  <div>
    <div class="orbit-header-left-label">NEWTON · TODAY</div>
    <div class="orbit-header-main">Executive Overview</div>
  </div>
  <div class="orbit-header-right-meta">AI snapshot · live</div>
</div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <style>
    /* إخفاء أزرار + و - من جميع حقول الأرقام */
    [data-testid="stNumberInput"] button {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
