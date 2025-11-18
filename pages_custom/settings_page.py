import os
from io import BytesIO
from datetime import datetime

import streamlit as st
from PIL import Image

# Optional: streamlit-cropper
try:
    from streamlit_cropper import st_cropper
except Exception:
    st_cropper = None




# ============================================================
#   SETTINGS PAGE (FULL, PROFESSIONAL, ADVANCED CONFIG MODE)
# ============================================================

def settings_app():

    st.markdown("<div class='section-title'>Settings</div>", unsafe_allow_html=True)

    # ----------------------------------------------------------
    #  ADVANCED MODE STATE
    # ----------------------------------------------------------
    if "advanced_mode" not in st.session_state:
        st.session_state.advanced_mode = False

    # ----------------------------------------------------------
    #  TOGGLE BUTTON
    # ----------------------------------------------------------
    if st.session_state.advanced_mode:
        if st.button("Disable Advanced Configuration"):
            st.session_state.advanced_mode = False
            st.rerun()
    else:
        if st.button("Enable Advanced Configuration"):
            st.session_state.advanced_mode = True
            st.rerun()

    # ----------------------------------------------------------
    #  ADVANCED MODE VISUALS (NO COLORS — respect global theme)
    # ----------------------------------------------------------
    if st.session_state.advanced_mode:
        st.markdown("""
        <style>
        .card-adv { padding: 18px; border-radius: 14px; margin-bottom: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.45); }
        * { transition: all 0.25s ease-in-out !important; }
        </style>
        """, unsafe_allow_html=True)

    # ============================================================
    #   BASIC SETTINGS (ALWAYS VISIBLE)
    # ============================================================
    st.markdown("<h4>General Settings</h4>", unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Company Name", "Newton Smart Home")
            company_phone = st.text_input("Company Phone", "+971 52 779 0975")
            company_email = st.text_input("Company Email", "info@newtonsmarthome.com")

        with col2:
            theme = st.selectbox("Theme Mode", ["Light", "Dark", "Auto"])

            # ----------------------------------------------
            # LOGO UPLOAD + CROP SECTION
            # ----------------------------------------------
            st.markdown("#### Company Logo")

            uploaded = st.file_uploader("Upload Logo (PNG / JPG / SVG)", type=["png","jpg","jpeg","svg"])

            # If user uploads a file
            if uploaded:
                ext = uploaded.name.lower().split(".")[-1]
                os.makedirs("data", exist_ok=True)

                # Case 1: SVG → save directly (no cropping needed)
                if ext == "svg":
                    save_path = "data/newton_logo.svg"
                    with open(save_path, "wb") as f:
                        f.write(uploaded.read())
                    st.success("SVG Logo saved successfully!")
                    st.markdown("Current logo:")
                    st.image(save_path, width=180)
                    st.rerun()

                # Case 2: PNG / JPG → allow cropping
                else:
                    # Robust open + convert to avoid mode issues
                    try:
                        img = Image.open(uploaded)
                    except Exception as e:
                        st.error(f"Could not open image: {e}")
                        st.stop()
                    if img.mode not in ("RGB", "RGBA"):
                        img = img.convert("RGBA")

                    if st_cropper is not None:
                        st.write("Crop your logo:")
                        cropped_img = st_cropper(
                            img,
                            realtime_update=True,
                            box_color="#0A84FF",
                            aspect_ratio=(1,1)
                        )

                        if st.button("Save Cropped Logo", use_container_width=True):
                            out_path = "data/newton_logo.png"
                            try:
                                mode_img = cropped_img
                                if mode_img.mode not in ("RGB", "RGBA"):
                                    mode_img = mode_img.convert("RGBA")
                                mode_img.save(out_path, format="PNG")
                            except Exception as e:
                                st.error(f"Failed to save logo: {e}")
                                st.stop()
                            st.success("Logo saved successfully!")
                            st.image(out_path, width=180)
                            st.rerun()
                    else:
                        st.info("Install 'streamlit-cropper' to enable cropping. Saving original image.")
                        if st.button("Save Logo", use_container_width=True):
                            out_path = "data/newton_logo.png"
                            try:
                                mode_img = img
                                if mode_img.mode not in ("RGB", "RGBA"):
                                    mode_img = mode_img.convert("RGBA")
                                mode_img.save(out_path, format="PNG")
                            except Exception as e:
                                st.error(f"Failed to save logo: {e}")
                                st.stop()
                            st.success("Logo saved successfully!")
                            st.image(out_path, width=180)
                            st.rerun()

            # Show existing logo if available (validate PNG to avoid PIL errors)
            st.markdown("#### Current Logo Preview")
            png_path = "data/newton_logo.png"
            svg_path = "data/newton_logo.svg"

            def _is_valid_image(path: str) -> bool:
                try:
                    with Image.open(path) as im:
                        im.verify()
                    return True
                except Exception:
                    return False

            if os.path.exists(png_path) and _is_valid_image(png_path):
                st.image(png_path, width=160)
            elif os.path.exists(svg_path):
                # Streamlit can display SVG in some environments; fallback to raw HTML if needed
                try:
                    st.image(svg_path, width=160)
                except Exception:
                    with open(svg_path, "r", encoding="utf-8", errors="ignore") as f:
                        svg_content = f.read()
                    st.markdown(f"<div style='width:160px'>{svg_content}</div>", unsafe_allow_html=True)
            elif os.path.exists(png_path) and not _is_valid_image(png_path):
                st.warning("Existing PNG logo is corrupted. Click to remove it and upload again.")
                if st.button("Remove Corrupted Logo"):
                    try:
                        os.remove(png_path)
                        st.success("Removed. Please upload a new logo.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not remove file: {e}")
            else:
                st.info("No logo found — upload a new one above.")


    st.markdown("---")

    # ============================================================
    #   ADVANCED MODE SECTIONS
    # ============================================================
    if st.session_state.advanced_mode:

        # ========================================================
        # 1) USER & ACCESS CONTROL
        # ========================================================
        with st.expander("User & Access Control"):
            st.markdown("<div class='card-adv'>", unsafe_allow_html=True)

            st.write("Manage system users and PIN codes.")

            new_user = st.text_input("Add new user")
            pin = st.text_input("Set PIN", type="password")

            if st.button("Create User"):
                st.success("User created (placeholder).")

            existing_users = ["Fahad (Admin)", "Ahmed (Sales)", "Omar (Viewer)"]
            selected = st.selectbox("Select User", existing_users)

            st.button("Reset PIN")
            st.button("Disable User")

            st.markdown("</div>", unsafe_allow_html=True)

        # ========================================================
        # 2) TEMPLATE ENGINE
        # ========================================================
        with st.expander("Templates Manager (DOCX)"):
            st.markdown("<div class='card-adv'>", unsafe_allow_html=True)

            st.write("Upload or manage quotation, invoice, and receipt templates.")

            temp = st.file_uploader("Upload Template (.docx)", type=["docx"])
            if temp:
                os.makedirs("data", exist_ok=True)
                with open(f"data/{temp.name}", "wb") as f:
                    f.write(temp.read())
                st.success("Template uploaded.")

            st.button("Reset to Default Templates")

            st.markdown("</div>", unsafe_allow_html=True)

        # ========================================================
        # 3) NUMBERING RULES
        # ========================================================
        with st.expander("Document Numbering Rules"):
            st.markdown("<div class='card-adv'>", unsafe_allow_html=True)

            q_prefix = st.text_input("Quotation Prefix", "Q-")
            i_prefix = st.text_input("Invoice Prefix", "I-")
            r_prefix = st.text_input("Receipt Prefix", "R-")
            auto_reset = st.selectbox("Reset Sequence", ["Daily","Monthly","Never"])

            st.button("Save Numbering Rules")

            st.markdown("</div>", unsafe_allow_html=True)

        # ========================================================
        # 4) DATA MANAGEMENT
        # ========================================================
        with st.expander("Data Backup & Export"):
            st.markdown("<div class='card-adv'>", unsafe_allow_html=True)

            st.write("Download or backup your full system data.")

            if st.button("Download Full Backup"):
                buf = BytesIO()
                # (placeholder)
                buf.write(b"Backup file content")
                st.download_button("Download backup.zip", buf, file_name="backup.zip")

            months = st.number_input("Delete records older than (months):", min_value=1, max_value=60)
            st.button("Clean Old Data")

            st.markdown("</div>", unsafe_allow_html=True)

        # ========================================================
        # 5) AI AUTOMATION
        # ========================================================
        with st.expander("AI Automation Settings"):
            st.markdown("<div class='card-adv'>", unsafe_allow_html=True)

            ai_enabled = st.checkbox("Enable AI Assistant")
            ai_permission = st.selectbox("Assistant Permission Level", ["Read-Only","Document Creation","Full Access"])

            ai_memory = st.checkbox("Allow Memory Storage")

            st.button("Save AI Configuration")

            st.markdown("</div>", unsafe_allow_html=True)

        # ========================================================
        # 6) SYSTEM LOGS
        # ========================================================
        with st.expander("System Logs"):
            st.markdown("<div class='card-adv'>", unsafe_allow_html=True)

            st.write("Last 100 events:")
            example_logs = [
                "2025-11-18 01:12 — User Login (Fahad)",
                "2025-11-18 01:10 — Invoice Generated",
                "2025-11-18 01:07 — Template Updated",
            ]
            st.code("\n".join(example_logs))

            st.button("Clear Logs")

            st.markdown("</div>", unsafe_allow_html=True)

        # ========================================================
        # 7) DANGER ZONE
        # ========================================================
        with st.expander("⚠️ Danger Zone"):
            st.markdown("""
            <div style="border:1px solid #ff453a;padding:16px;border-radius:12px;color:#ff453a;">
            <h4>Danger Zone</h4>
            """, unsafe_allow_html=True)

            st.write("These actions cannot be undone.")

            colA, colB = st.columns(2)
            with colA:
                st.button("Reset Entire System")
            with colB:
                st.button("Delete All Data")

            st.markdown("</div>", unsafe_allow_html=True)


# --------------------------------------------------------------
# END OF SETTINGS PAGE
# --------------------------------------------------------------
