import streamlit as st
import pandas as pd
import os
from io import BytesIO
from datetime import datetime

# ==========================================
# EXCEL FILE AUTO-CREATION
# ==========================================
import pandas as pd
import os

def ensure_product_file():
    if not os.path.exists("data"):
        os.makedirs("data")

    products_path = "data/products.xlsx"

    # If file missing → create default structure
    if not os.path.exists(products_path):
        df = pd.DataFrame(columns=[
            "Device",          # product name
            "Description",     # short explanation
            "UnitPrice",       # default price
            "Warranty"         # years
        ])
        df.to_excel(products_path, index=False)

# ==========================================
# HELPERS
# ==========================================

def proper_case(text):
    if text is None:
        return ""
    try:
        return str(text).strip().title()
    except Exception:
        return str(text)


def load_products():
    ensure_product_file()
    try:
        df = pd.read_excel("data/products.xlsx")
        # normalize mandatory columns
        for col in ["Device", "Description", "UnitPrice", "Warranty"]:
            if col not in df.columns:
                df[col] = None
        return df[["Device", "Description", "UnitPrice", "Warranty"]]
    except Exception:
        return pd.DataFrame(columns=["Device", "Description", "UnitPrice", "Warranty"])


def save_products(df: pd.DataFrame):
    os.makedirs("data", exist_ok=True)
    # ensure correct columns and order
    for col in ["Device", "Description", "UnitPrice", "Warranty"]:
        if col not in df.columns:
            df[col] = None
    df = df[["Device", "Description", "UnitPrice", "Warranty"]]
    df.to_excel("data/products.xlsx", index=False)


# ==========================================
# MAIN PAGE CONTENT
# ==========================================

def products_app():
    ensure_product_file()

    st.markdown("<div class='section-title'>Products</div>", unsafe_allow_html=True)

    # Local CSS to fix header widths and compact rows (avoid invoice overrides)
    st.markdown(
        """
        <style>
        .products-header{
            display:flex; gap:1rem; padding:8px 0 12px;
            border-bottom:1px solid rgba(0,0,0,.08); background:transparent;
            font-size:11px; font-weight:600; letter-spacing:.06em; text-transform:uppercase; color:#86868b;
            margin-bottom:10px; align-items:center;
        }
        .products-header span{text-align:center;}
        .products-header span:nth-child(1){flex:2.4; text-align:left;}
        .products-header span:nth-child(2){flex:3.6; text-align:left;}
        .products-header span:nth-child(3){flex:1;}
        .products-header span:nth-child(4){flex:1;}
        .products-header span:nth-child(5){flex:1;}

        .added-product-row{ background:#fff; padding:8px 12px; border:1px solid rgba(0,0,0,.08); border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,.05); }
        .product-value{ font-weight:600; color:#1d1d1f; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --------------- SEARCH ----------------
    s1, s2 = st.columns([2, 2])
    with s1:
        q_device = st.text_input("Search by Device")
    with s2:
        q_desc = st.text_input("Search by Description")

    df = load_products()

    # Filter by search
    fdf = df.copy()
    if q_device:
        ql = q_device.strip().lower()
        fdf = fdf[fdf["Device"].astype(str).str.lower().str.contains(ql, na=False)]
    if q_desc:
        ql2 = q_desc.strip().lower()
        fdf = fdf[fdf["Description"].astype(str).str.lower().str.contains(ql2, na=False)]

    # --------------- TABLE (compact rows with actions) ----------------
    st.markdown("<div class='section-title'>Catalog</div>", unsafe_allow_html=True)

    # Table Header
    st.markdown(
        """
        <div class="product-header products-header">
            <span>Device</span>
            <span>Description</span>
            <span>Unit Price (AED)</span>
            <span>Warranty (Years)</span>
            <span>Actions</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if fdf.empty:
        st.info("No products found. Add your first product below.")
    else:
        for idx, row in fdf.reset_index(drop=True).iterrows():
            dcol = st.columns([2.4, 3.6, 1.0, 1.0, 1.0])
            with dcol[0]:
                st.markdown(f"<div class='added-product-row' style='padding:8px 12px;'><span class='product-value' style='font-size:13px'>{row['Device']}</span></div>", unsafe_allow_html=True)
            with dcol[1]:
                st.markdown(f"<div class='added-product-row' style='padding:8px 12px;font-size:13px'>{row['Description']}</div>", unsafe_allow_html=True)
            with dcol[2]:
                try:
                    price_txt = f"{float(row['UnitPrice']):,.2f}"
                except Exception:
                    price_txt = str(row['UnitPrice'])
                st.markdown(f"<div class='added-product-row' style='padding:8px 12px;'><span class='product-value' style='font-size:13px'>{price_txt}</span></div>", unsafe_allow_html=True)
            with dcol[3]:
                try:
                    war_txt = f"{int(row['Warranty'])}"
                except Exception:
                    war_txt = str(row['Warranty'])
                st.markdown(f"<div class='added-product-row' style='padding:8px 12px;'><span class='product-value' style='font-size:13px'>{war_txt}</span></div>", unsafe_allow_html=True)
            with dcol[4]:
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✏️", key=f"edit_{idx}"):
                        st.session_state["_prod_edit_idx"] = int(df.index[fdf.index[idx]]) if not fdf.empty else None
                        st.session_state["_prod_mode"] = "edit"
                        st.rerun()
                with c2:
                    if st.button("🗑️", key=f"del_{idx}"):
                        st.session_state["_prod_delete_idx"] = int(df.index[fdf.index[idx]])
                        st.session_state["_prod_mode"] = "confirm_delete"
                        st.rerun()

    # --------------- CONFIRM DELETE ----------------
    if st.session_state.get("_prod_mode") == "confirm_delete":
        del_idx = st.session_state.get("_prod_delete_idx")
        if del_idx is not None and 0 <= del_idx < len(df):
            st.warning(f"Confirm delete: {df.iloc[del_idx]['Device']}")
            cdel1, cdel2 = st.columns(2)
            with cdel1:
                if st.button("Yes, Delete"):
                    new_df = df.drop(df.index[del_idx]).reset_index(drop=True)
                    save_products(new_df)
                    st.success("Product deleted")
                    st.session_state.pop("_prod_delete_idx", None)
                    st.session_state.pop("_prod_mode", None)
                    st.rerun()
            with cdel2:
                if st.button("Cancel"):
                    st.session_state.pop("_prod_delete_idx", None)
                    st.session_state.pop("_prod_mode", None)
                    st.rerun()

    # --------------- ADD / EDIT FORMS ----------------
    st.markdown("---")

    mode = st.session_state.get("_prod_mode", "add")
    if mode == "edit":
        st.markdown("<div class='section-title'>Edit Product</div>", unsafe_allow_html=True)
        edit_idx = st.session_state.get("_prod_edit_idx")
        if edit_idx is not None and 0 <= edit_idx < len(df):
            er1, er2 = st.columns(2)
            with er1:
                e_device = st.text_input("Device", value=df.iloc[edit_idx]["Device"], key="_e_dev")
                e_price = st.number_input("UnitPrice", min_value=0.0, value=float(df.iloc[edit_idx]["UnitPrice"]) if pd.notna(df.iloc[edit_idx]["UnitPrice"]) else 0.0, step=10.0, key="_e_price")
            with er2:
                e_warranty = st.number_input("Warranty", min_value=0, value=int(df.iloc[edit_idx]["Warranty"]) if pd.notna(df.iloc[edit_idx]["Warranty"]) else 0, step=1, key="_e_war")
                e_desc = st.text_area("Description", value=str(df.iloc[edit_idx]["Description"]), height=90, key="_e_desc")

            ec1, ec2, ec3 = st.columns([1,1,2])
            with ec1:
                if st.button("Save Changes"):
                    # check unique (excluding self)
                    cand = proper_case(e_device)
                    dup = df[(df.index != edit_idx) & (df["Device"].astype(str).str.strip().str.lower() == cand.strip().lower())]
                    if not cand.strip():
                        st.warning("Device is required.")
                    elif not dup.empty:
                        st.warning("Device must be unique.")
                    else:
                        df.loc[edit_idx, ["Device","Description","UnitPrice","Warranty"]] = [proper_case(e_device), e_desc, e_price, e_warranty]
                        save_products(df)
                        st.success("Product updated")
                        st.session_state.pop("_prod_edit_idx", None)
                        st.session_state["_prod_mode"] = "add"
                        st.rerun()
            with ec2:
                if st.button("Cancel Edit"):
                    st.session_state.pop("_prod_edit_idx", None)
                    st.session_state["_prod_mode"] = "add"
                    st.rerun()
    else:
        st.markdown("<div class='section-title'>Add New Product</div>", unsafe_allow_html=True)
        ar1, ar2 = st.columns(2)
        with ar1:
            a_device = st.text_input("Device", value="", key="_a_dev")
            a_price = st.number_input("UnitPrice", min_value=0.0, step=10.0, value=0.0, key="_a_price")
        with ar2:
            a_warranty = st.number_input("Warranty", min_value=0, step=1, value=0, key="_a_war")
            a_desc = st.text_area("Description", value="", height=90, key="_a_desc")

        ac1, ac2, ac3 = st.columns([1,1,2])
        with ac1:
            if st.button("Add Product"):
                cand = proper_case(a_device)
                if not cand.strip():
                    st.warning("Device is required.")
                elif not df[df["Device"].astype(str).str.strip().str.lower() == cand.strip().lower()].empty:
                    st.warning("Device must be unique.")
                else:
                    new_row = {
                        "Device": cand,
                        "Description": a_desc,
                        "UnitPrice": a_price,
                        "Warranty": a_warranty,
                    }
                    new_df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    save_products(new_df)
                    st.success("Product added")
                    st.rerun()
        with ac2:
            if st.button("Reset Form"):
                st.session_state["_a_dev"] = ""
                st.session_state["_a_price"] = 0.0
                st.session_state["_a_war"] = 0
                st.session_state["_a_desc"] = ""
                st.rerun()

    # --------------- EXTRA FEATURES ----------------
    st.markdown("---")
    st.markdown("<div class='section-title'>Import / Export</div>", unsafe_allow_html=True)

    # Export current dataframe
    buf = BytesIO()
    fdf[["Device","Description","UnitPrice","Warranty"]].to_excel(buf, index=False)
    buf.seek(0)
    st.download_button("Download Products (Excel)", data=buf, file_name=f"products_export_{datetime.today().strftime('%Y%m%d')}.xlsx")

    # Import uploader
    up = st.file_uploader("Upload products.xlsx", type=["xlsx"], accept_multiple_files=False)
    if up is not None:
        try:
            imp = pd.read_excel(up)
            # Validate required columns
            for col in ["Device","Description","UnitPrice","Warranty"]:
                if col not in imp.columns:
                    st.error(f"Missing column in uploaded file: {col}")
                    return
            st.warning("This will replace all existing products.")
            ic1, ic2 = st.columns(2)
            with ic1:
                if st.button("Confirm Replace"):
                    # Normalize device names to proper case and ensure correct order
                    imp["Device"] = imp["Device"].apply(proper_case)
                    save_products(imp[["Device","Description","UnitPrice","Warranty"]])
                    st.success("Products replaced from upload.")
                    st.rerun()
            with ic2:
                if st.button("Cancel Import"):
                    st.rerun()
        except Exception as e:
            st.error(f"Failed to read uploaded file: {e}")
