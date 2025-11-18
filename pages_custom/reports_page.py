import os
from io import BytesIO
from datetime import datetime, date
from typing import Tuple

import pandas as pd
import streamlit as st
import altair as alt

# ==========================================
# File Ensurers
# ==========================================

def ensure_report_files():
    os.makedirs("data", exist_ok=True)

    cust_path = "data/customers.xlsx"
    rec_path = "data/records.xlsx"

    if not os.path.exists(cust_path):
        pd.DataFrame(columns=[
            "client_name","phone","location","email","status",
            "notes","tags","next_follow_up","assigned_to","last_activity"
        ]).to_excel(cust_path, index=False)

    if not os.path.exists(rec_path):
        pd.DataFrame(columns=[
            "base_id","date","type","number","amount","client_name","phone","location","note"
        ]).to_excel(rec_path, index=False)

# ==========================================
# Loaders with normalization
# ==========================================

def _load_records() -> pd.DataFrame:
    ensure_report_files()
    try:
        df = pd.read_excel("data/records.xlsx")
        df.columns = [c.strip().lower() for c in df.columns]
        # Normalize types and dates
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if "type" in df.columns:
            df["type"] = df["type"].astype(str).str.lower()
        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "base_id","date","type","number","amount","client_name","phone","location","note"
        ])


def _load_customers() -> pd.DataFrame:
    try:
        df = pd.read_excel("data/customers.xlsx")
        df.columns = [c.strip().lower() for c in df.columns]
        if "next_follow_up" in df.columns:
            df["next_follow_up"] = pd.to_datetime(df["next_follow_up"], errors="coerce")
        return df
    except Exception:
        return pd.DataFrame(columns=[
            "client_name","phone","location","email","status",
            "notes","tags","next_follow_up","assigned_to","last_activity"
        ])


def _load_products() -> pd.DataFrame:
    try:
        df = pd.read_excel("data/products.xlsx")
        return df
    except Exception:
        return pd.DataFrame()

# ==========================================
# Filters
# ==========================================

UAE_LOCATIONS = [
    "Abu Dhabi - Al Shamkha","Abu Dhabi - Al Shawamekh","Abu Dhabi - Khalifa City",
    "Abu Dhabi - Al Bateen","Abu Dhabi - Al Reem Island","Abu Dhabi - Yas Island",
    "Abu Dhabi - Al Mushrif","Abu Dhabi - Al Rawdah","Abu Dhabi - Al Muroor",
    "Abu Dhabi - Baniyas","Abu Dhabi - Mussafah","Abu Dhabi - Al Mafraq",
    "Abu Dhabi - Al Falah","Abu Dhabi - MBZ City","Abu Dhabi - Al Raha",
    "Abu Dhabi - Al Maqtaa","Abu Dhabi - Zayed Port","Abu Dhabi - Saadiyat Island",
    "Al Ain - Al Jimi","Al Ain - Falaj Hazza","Al Ain - Al Maqam",
    "Al Ain - Zakher","Al Ain - Hili","Al Ain - Al Foah","Al Ain - Al Mutaredh",
    "Al Ain - Al Towayya","Al Ain - Al Sarooj","Al Ain - Al Nyadat",
    "Dubai - Marina","Dubai - Downtown","Dubai - Business Bay",
    "Dubai - Jumeirah","Dubai - JBR","Dubai - Al Barsha","Dubai - Mirdif",
    "Dubai - Deira","Dubai - Bur Dubai","Dubai - Silicon Oasis",
    "Dubai - Academic City","Dubai - Arabian Ranches","Dubai - International City",
    "Dubai - Dubai Hills","Dubai - The Springs","Dubai - The Meadows",
    "Dubai - The Greens","Dubai - Palm Jumeirah","Dubai - Al Qusais",
    "Dubai - Al Nahda","Dubai - JVC","Dubai - Damac Hills",
    "Dubai - Discovery Gardens","Dubai - IMPZ","Dubai - Al Warqa",
    "Dubai - Nad Al Sheba",
    "Sharjah - Al Majaz","Sharjah - Al Nahda","Sharjah - Al Taawun",
    "Sharjah - Muwaileh","Sharjah - Al Khan","Sharjah - Al Yarmook",
    "Sharjah - Al Qasimia","Sharjah - Al Fisht","Sharjah - Al Nasserya",
    "Sharjah - Al Goaz","Sharjah - Al Jubail","Sharjah - Maysaloon",
    "Ajman - Al Rashidiya","Ajman - Al Nuaimiya","Ajman - Al Mowaihat",
    "Ajman - Al Rawda","Ajman - Al Jurf","Ajman - Al Hamidiya",
    "Ajman - Al Rumailah","Ajman - Al Bustan","Ajman - City Center",
    "RAK - Al Nakheel","RAK - Al Dhait","RAK - Julph",
    "RAK - Khuzam","RAK - Al Qusaidat","RAK - Seih Al Uraibi",
    "RAK - Al Rams","RAK - Al Mairid","RAK - Mina Al Arab",
    "RAK - Al Hamra Village","RAK - Marjan Island",
    "Fujairah - Al Faseel","Fujairah - Madhab","Fujairah - Dibba",
    "Fujairah - Sakamkam","Fujairah - Mirbah","Fujairah - Al Taween",
    "Fujairah - Kalba","Fujairah - Qidfa","Fujairah - Al Aqah",
    "UAQ - Al Salama","UAQ - Al Haditha","UAQ - Al Raas",
    "UAQ - Al Dar Al Baida","UAQ - Al Khor","UAQ - Al Ramlah",
    "UAQ - Al Maidan","UAQ - Emirates City",
]


def _apply_filters(records: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    st.markdown("<div class='section-title'>Filters</div>", unsafe_allow_html=True)

    # Default date range: this year
    today = date.today()
    start_default = date(today.year, 1, 1)
    end_default = today

    f1, f2, f3 = st.columns([1.2, 1, 1])
    with f1:
        start_date = st.date_input("Start Date", start_default)
        end_date = st.date_input("End Date", end_default)
    with f2:
        doc_type = st.selectbox("Document Type", ["All", "Quotation", "Invoice", "Receipt"], index=0)
        name_kw = st.text_input("Customer Name contains")
    with f3:
        location = st.selectbox("Location", ["All"] + UAE_LOCATIONS, index=0)
        min_amt, max_amt = st.columns(2)
        with min_amt:
            amt_min = st.number_input("Min Amount", min_value=0.0, value=0.0, step=100.0)
        with max_amt:
            amt_max = st.number_input("Max Amount", min_value=0.0, value=0.0, step=100.0)

    # Build mask
    m = pd.Series([True] * len(records))
    if not records.empty:
        if "date" in records.columns:
            m &= (records["date"].dt.date >= start_date) & (records["date"].dt.date <= end_date)
        if doc_type != "All" and "type" in records.columns:
            map_type = {"Quotation": "q", "Invoice": "i", "Receipt": "r"}
            m &= records["type"].isin([map_type.get(doc_type, "")])
        if name_kw:
            m &= records.get("client_name", pd.Series([""]*len(records))).astype(str).str.contains(name_kw, case=False, na=False)
        if location != "All":
            m &= records.get("location", pd.Series([""]*len(records))).astype(str) == location
        if amt_min > 0:
            m &= records.get("amount", pd.Series([0]*len(records))).astype(float) >= amt_min
        if amt_max > 0:
            m &= records.get("amount", pd.Series([0]*len(records))).astype(float) <= amt_max

    filtered = records[m].copy() if not records.empty else records.copy()
    return filtered, {
        "start": start_date, "end": end_date, "doc_type": doc_type,
        "name_kw": name_kw, "location": location, "amt_min": amt_min, "amt_max": amt_max,
    }

# ==========================================
# Metrics
# ==========================================


def _metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div class='hero-card' style='padding:16px'>
            <div style='font-size:12px;color:#6e6e73;font-weight:700;text-transform:uppercase;letter-spacing:.06em'>{label}</div>
            <div style='font-size:26px;font-weight:800;margin-top:6px'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ==========================================
# Main App
# ==========================================

def reports_app():
    ensure_report_files()
    records = _load_records()
    customers = _load_customers()
    products = _load_products()

    # 1) Filters
    filtered, fvals = _apply_filters(records)

    # 2) Summary metrics
    st.markdown("<div class='section-title'>Summary</div>", unsafe_allow_html=True)
    q_count = int(filtered[filtered["type"] == "q"].shape[0]) if not filtered.empty else 0
    inv_sum = float(filtered[filtered["type"] == "i"]["amount"].sum()) if not filtered.empty else 0.0
    rec_sum = float(filtered[filtered["type"] == "r"]["amount"].sum()) if not filtered.empty else 0.0
    outstanding = inv_sum - rec_sum
    projects = filtered["base_id"].nunique() if "base_id" in filtered.columns else 0

    # Top customer by revenue (invoice sum)
    top_customer = "—"
    if not filtered.empty:
        inv_by_cust = filtered[filtered["type"] == "i"].groupby("client_name", dropna=False)["amount"].sum().sort_values(ascending=False)
        if not inv_by_cust.empty:
            top_customer = f"{inv_by_cust.index[0]} (AED {inv_by_cust.iloc[0]:,.0f})"

    c1, c2, c3, c4, c5 = st.columns(5)
    _metric_card.__wrapped__ = _metric_card  # appease lints
    with c1: _metric_card("Total Quotations", f"{q_count:,}")
    with c2: _metric_card("Total Invoice Amount", f"{inv_sum:,.2f} AED")
    with c3: _metric_card("Total Received Amount", f"{rec_sum:,.2f} AED")
    with c4: _metric_card("Outstanding Balance", f"{outstanding:,.2f} AED")
    with c5: _metric_card("Top Customer", top_customer)

    # 3) Documents table
    st.markdown("---")
    st.markdown("<div class='section-title'>Documents</div>", unsafe_allow_html=True)

    if not filtered.empty:
        view = filtered.copy()
        # Order columns for view
        cols = [
            "date","type","number","client_name","phone","location","amount","base_id","note"
        ]
        cols = [c for c in cols if c in view.columns]
        view = view[cols].sort_values(by=["date"], ascending=False)
        st.dataframe(view, use_container_width=True, hide_index=True)

        # Exports
        buf_xlsx = BytesIO()
        view.to_excel(buf_xlsx, index=False)
        buf_xlsx.seek(0)
        st.download_button("Export Excel", buf_xlsx, file_name="documents_report.xlsx")

        buf_csv = BytesIO(view.to_csv(index=False).encode("utf-8"))
        st.download_button("Export CSV", buf_csv, file_name="documents_report.csv")
    else:
        st.info("No documents match your filters.")

    # 4) Financial analytics
    st.markdown("---")
    st.markdown("<div class='section-title'>Financial Analytics</div>", unsafe_allow_html=True)

    if not filtered.empty and "date" in filtered.columns:
        df_i = filtered[filtered["type"] == "i"][['date','amount']].copy()
        df_r = filtered[filtered["type"] == "r"][['date','amount']].copy()
        if not df_i.empty:
            df_i['month'] = df_i['date'].dt.to_period('M').dt.to_timestamp()
            inv_month = df_i.groupby('month')['amount'].sum().reset_index()
            chart_i = alt.Chart(inv_month).mark_bar(color="#0a84ff").encode(x='month:T', y='amount:Q').properties(height=220)
            st.altair_chart(chart_i, use_container_width=True)
        else:
            st.info("No invoices in range for Monthly Revenue chart.")

        if not df_r.empty:
            df_r['month'] = df_r['date'].dt.to_period('M').dt.to_timestamp()
            rec_month = df_r.groupby('month')['amount'].sum().reset_index()
            chart_r = alt.Chart(rec_month).mark_area(color="#34c759", opacity=0.5).encode(x='month:T', y='amount:Q').properties(height=220)
            st.altair_chart(chart_r, use_container_width=True)
        else:
            st.info("No receipts in range for Monthly Collection chart.")

        # Outstanding pie
        paid = float(rec_sum)
        invoiced = float(inv_sum)
        remain = max(invoiced - paid, 0.0)
        pie_df = pd.DataFrame({
            'status': ['Paid','Unpaid'],
            'value': [paid, remain]
        })
        pie = alt.Chart(pie_df).mark_arc(innerRadius=60).encode(
            theta='value:Q', color=alt.Color('status:N', scale=alt.Scale(range=['#34c759','#ff3b30']))
        ).properties(height=250)
        st.altair_chart(pie, use_container_width=True)
    else:
        st.info("Not enough data for charts.")

    # 5) Top customers
    st.markdown("---")
    st.markdown("<div class='section-title'>Top Customers</div>", unsafe_allow_html=True)
    if not records.empty:
        inv = records[records['type'] == 'i']
        rec = records[records['type'] == 'r']
        inv_by = inv.groupby('client_name', dropna=False)['amount'].sum().rename('Total Invoiced')
        rec_by = rec.groupby('client_name', dropna=False)['amount'].sum().rename('Total Paid')
        top = pd.concat([inv_by, rec_by], axis=1).fillna(0.0)
        top['Balance'] = top['Total Invoiced'] - top['Total Paid']
        top = top.sort_values('Total Invoiced', ascending=False).reset_index().rename(columns={'client_name':'Customer Name'})
        st.dataframe(top, use_container_width=True, hide_index=True)

        # Optional horizontal bar chart by invoiced
        if not top.empty:
            chart_top = alt.Chart(top).mark_bar(color="#0a84ff").encode(
                x='Total Invoiced:Q', y=alt.Y('Customer Name:N', sort='-x')
            ).properties(height=300)
            st.altair_chart(chart_top, use_container_width=True)
    else:
        st.info("No invoice/receipt data available yet.")

    # 6) Top products (placeholder)
    st.markdown("---")
    st.markdown("<div class='section-title'>Top Products (coming soon)</div>", unsafe_allow_html=True)
    if products.empty:
        st.caption("Products file is empty or not linked to records yet.")
    else:
        st.caption("Future: aggregate line-items from documents.")

    # 7) Customer follow-up report
    st.markdown("---")
    st.markdown("<div class='section-title'>Customer Follow-up</div>", unsafe_allow_html=True)
    if not customers.empty:
        today = pd.to_datetime(date.today())
        need_follow = customers[(customers.get('status','').astype(str).str.lower() == 'follow-up') |
                                (customers.get('next_follow_up').notna() & (customers['next_follow_up'] <= today))]
        cols = [
            'client_name','phone','location','assigned_to','status','next_follow_up','notes'
        ]
        cols = [c for c in cols if c in need_follow.columns]
        st.dataframe(need_follow[cols], use_container_width=True, hide_index=True)
    else:
        st.info("No customers found.")

    # 8) Exporting
    st.markdown("---")
    st.markdown("<div class='section-title'>Exporting</div>", unsafe_allow_html=True)

    # Full report = filtered documents as Excel
    full_buf = BytesIO()
    (filtered if not filtered.empty else records).to_excel(full_buf, index=False)
    full_buf.seek(0)
    st.download_button("Download Full Report (Excel)", full_buf, file_name="full_report.xlsx")

    # Summary only
    summary_df = pd.DataFrame([
        {"Metric":"Total Quotations","Value": q_count},
        {"Metric":"Total Invoice Amount","Value": inv_sum},
        {"Metric":"Total Received Amount","Value": rec_sum},
        {"Metric":"Outstanding Balance","Value": outstanding},
        {"Metric":"Total Projects","Value": projects},
        {"Metric":"Top Customer","Value": top_customer},
    ])
    sum_buf = BytesIO()
    summary_df.to_excel(sum_buf, index=False)
    sum_buf.seek(0)
    st.download_button("Download Summary Only (Excel)", sum_buf, file_name="summary_report.xlsx")
