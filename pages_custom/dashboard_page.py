import streamlit as st
import pandas as pd
from datetime import datetime

# ---------- THEME (Premium Apple Design) ----------
def _apply_dashboard_theme():
    st.markdown(
        """
        <style>
        /* Icon grid */
        #dashboard-icons .row{
            display:grid; 
            grid-template-columns: repeat(7, 1fr); 
            gap:16px; 
            margin:12px 0 24px;
        }
        #dashboard-icons [data-testid="stButton"] > button{
            width:100%;
            white-space: pre-line;
            text-align:center;
            padding: 20px 12px 16px;
            border-radius: 20px;
            background: linear-gradient(145deg, #ffffff 0%, #f9f9fb 100%) !important;
            border: 1px solid rgba(0,0,0,.08) !important;
            color: var(--ink) !important;
            box-shadow: 
                0 1px 3px rgba(0,0,0,.06),
                0 8px 24px rgba(0,0,0,.08),
                inset 0 1px 0 rgba(255,255,255,.6) !important;
            font-weight: 600;
            font-size: 13px;
            transition: all .2s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
        }
        #dashboard-icons [data-testid="stButton"] > button:hover{
            transform: translateY(-4px) scale(1.02);
            box-shadow: 
                0 2px 6px rgba(0,0,0,.08),
                0 16px 40px rgba(0,0,0,.12),
                inset 0 1px 0 rgba(255,255,255,.8) !important;
            border-color: rgba(10,132,255,.25) !important;
            background: linear-gradient(145deg, #f0f8ff 0%, #ffffff 100%) !important;
        }
        #dashboard-icons [data-testid="stButton"] > button:active{
            transform: translateY(-1px) scale(1);
            box-shadow: 
                0 1px 4px rgba(0,0,0,.1),
                0 8px 20px rgba(0,0,0,.1) !important;
        }
        #dashboard-icons [data-testid="stButton"] > button::first-line{ 
            font-size: 32px; 
            line-height: 1.2;
        }

        /* Metric cards */
        .metric{
            background: linear-gradient(145deg, rgba(255,255,255,.92) 0%, rgba(250,250,252,.88) 100%);
            border:1px solid rgba(0,0,0,.06);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 
                0 2px 8px rgba(0,0,0,.04),
                0 12px 32px rgba(0,0,0,.06);
            backdrop-filter: blur(20px);
            position: relative;
            overflow: hidden;
        }
        .metric::before{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 4px; height: 100%;
            background: linear-gradient(180deg, var(--accent), var(--accent-light));
            opacity: 0;
            transition: opacity .3s ease;
        }
        .metric:hover::before{ opacity: 1; }
        .metric .label{
            font-size:11px; 
            letter-spacing:.08em; 
            text-transform:uppercase; 
            color:#86868b;
            font-weight: 600;
        }
        .metric .row{
            display:flex; 
            align-items:baseline; 
            gap:10px; 
            margin-top:8px;
        }
        .metric .value{
            font-size:32px; 
            font-weight:700;
            background: linear-gradient(135deg, #1d1d1f 0%, #515154 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .metric .sub{color:#86868b; font-size:13px;}

        /* Tables */
        .table-wrap{
            background: linear-gradient(145deg, rgba(255,255,255,.92), rgba(250,250,252,.88));
            border:1px solid rgba(0,0,0,.06);
            border-radius: 18px;
            padding: 16px 20px;
            box-shadow: 
                0 2px 8px rgba(0,0,0,.04),
                0 12px 28px rgba(0,0,0,.06);
            backdrop-filter: blur(16px);
        }

        /* Streamlit table styling */
        [data-testid="stTable"]{
            background: transparent !important;
        }
        [data-testid="stTable"] table{
            border-collapse: separate;
            border-spacing: 0;
        }
        [data-testid="stTable"] th{
            background: rgba(0,0,0,.02);
            color: var(--sub);
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: .05em;
            padding: 10px 12px;
            border-bottom: 1px solid rgba(0,0,0,.06);
        }
        [data-testid="stTable"] td{
            padding: 12px;
            border-bottom: 1px solid rgba(0,0,0,.04);
            color: var(--ink);
            font-size: 14px;
        }
        [data-testid="stTable"] tr:last-child td{
            border-bottom: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------- DATA HELPERS ----------
def _load_or_empty(path, columns):
    try:
        df = pd.read_excel(path)
        df.columns = [c.strip().lower() for c in df.columns]
    except Exception:
        df = pd.DataFrame(columns=columns)
    return df

def _metric(label, value, sub=""):
    st.markdown(
        f"""
        <div class="metric">
          <div class="label">{label}</div>
          <div class="row">
            <div class="value">{value}</div>
          </div>
          <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def _app_icon_grid():
    items = [
        ("📄\nQuotations", "quotation"),
        ("💳\nInvoices",   "invoice"),
        ("🧾\nReceipts",   "receipt"),
        ("👥\nCustomers",  "customers"),
        ("📦\nProducts",   "products"),
        ("📊\nReports",    "reports"),
        ("⚙️\nSettings",   "settings"),
    ]
    st.markdown('<div id="dashboard-icons"><div class="row">', unsafe_allow_html=True)
    cols = st.columns(len(items))
    for i, (c, (label, target)) in enumerate(zip(cols, items)):
        with c:
            if st.button(label, key=f"dash_nav_{target}_{i}", use_container_width=True):
                st.session_state["active_page"] = target
                st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------- MAIN ----------
def dashboard_app():
    _apply_dashboard_theme()


    _app_icon_grid()

    records = _load_or_empty(
        "data/records.xlsx",
        ["base_id", "date", "type", "number", "amount", "client_name", "phone", "location", "note"],
    )
    customers = _load_or_empty(
        "data/customers.xlsx",
        ["client_name", "phone", "location", "last_activity", "status"],
    )

    rec = records.copy()
    if not rec.empty and "date" in rec.columns:
        rec["date"] = pd.to_datetime(rec["date"], errors="coerce")

    total_q = int((rec["type"] == "q").sum()) if "type" in rec.columns else 0
    total_i = int((rec["type"] == "i").sum()) if "type" in rec.columns else 0
    total_r = int((rec["type"] == "r").sum()) if "type" in rec.columns else 0
    total_invoice_amount = float(rec.loc[rec.get("type","") == "i", "amount"].sum()) if "amount" in rec.columns else 0.0
    total_received = float(rec.loc[rec.get("type","") == "r", "amount"].sum()) if "amount" in rec.columns else 0.0
    remaining_balance = total_invoice_amount - total_received

    c1, c2, c3 = st.columns(3)
    with c1: _metric("Quotations", total_q, "Active proposals")
    with c2: _metric("Invoices", total_i, "Issued bills")
    with c3: _metric("Receipts", total_r, "Recorded payments")

    c4, c5, c6 = st.columns(3)
    with c4: _metric("Invoice Volume", f"AED {total_invoice_amount:,.0f}")
    with c5: _metric("Received", f"AED {total_received:,.0f}")
    with c6: _metric("Outstanding", f"AED {remaining_balance:,.0f}")

    st.markdown('<div class="section-title">Top Clients</div>', unsafe_allow_html=True)
    st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
    if not rec.empty and {"type","amount","client_name"}.issubset(rec.columns):
        top_clients = (
            rec[rec["type"] == "i"]
            .groupby("client_name")["amount"]
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
        )
        if not top_clients.empty:
            st.table(top_clients.rename(columns={"client_name": "Client", "amount": "Amount (AED)"}))
        else:
            st.write("No invoice data available.")
    else:
        st.write("No invoice data available.")
    st.markdown('</div>', unsafe_allow_html=True)

    two1, two2 = st.columns(2)
    with two1:
        st.markdown('<div class="section-title">Latest Invoices</div>', unsafe_allow_html=True)
        st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
        if not rec.empty and "type" in rec.columns:
            last_10_invoices = (
                rec[rec["type"] == "i"]
                .sort_values("date", ascending=False, na_position="last")
                .head(10)[["date", "number", "client_name", "amount"]]
            )
            if not last_10_invoices.empty:
                d = last_10_invoices.copy()
                if "date" in d.columns:
                    d["date"] = pd.to_datetime(d["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                st.table(d.rename(columns={"date": "Date", "number": "Invoice", "client_name": "Client", "amount": "Amount (AED)"}))
            else:
                st.write("No invoices yet.")
        else:
            st.write("No invoices yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with two2:
        st.markdown('<div class="section-title">Latest Receipts</div>', unsafe_allow_html=True)
        st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
        if not rec.empty and "type" in rec.columns:
            last_10_receipts = (
                rec[rec["type"] == "r"]
                .sort_values("date", ascending=False, na_position="last")
                .head(10)[["date", "number", "client_name", "amount"]]
            )
            if not last_10_receipts.empty:
                d = last_10_receipts.copy()
                if "date" in d.columns:
                    d["date"] = pd.to_datetime(d["date"], errors="coerce").dt.strftime("%Y-%m-%d")
                st.table(d.rename(columns={"date": "Date", "number": "Receipt", "client_name": "Client", "amount": "Amount (AED)"}))
            else:
                st.write("No receipts yet.")
        else:
            st.write("No receipts yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Customer Signals</div>', unsafe_allow_html=True)
    st.markdown('<div class="table-wrap">', unsafe_allow_html=True)
    if not customers.empty:
        st.table(
            customers.rename(
                columns={
                    "client_name": "Client",
                    "phone": "Phone",
                    "location": "Location",
                    "last_activity": "Last Activity",
                    "status": "Stage",
                }
            )
        )
    else:
        st.write("No customer records yet.")
    st.markdown('</div>', unsafe_allow_html=True)
