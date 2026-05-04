import streamlit as st
from src.db import database


def render():
    database.init_db()

    st.title("TD Accessibility Document Checker")
    st.markdown(
        "This tool helps your team check documents for accessibility compliance before they are "
        "published as PDFs. It is based on **ISO 14289-1 (PDF/UA)** and the **Matterhorn Protocol**."
    )

    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("Step 1 — Pre-flight Check")
        st.write(
            "Upload a **Word (.docx)**, **PowerPoint (.pptx)**, or **PDF** file to get a plain-English "
            "list of accessibility issues that need to be fixed before final export."
        )
        st.markdown("**Accepts:** `.docx` `.pptx` `.pdf`")
        if st.button("Go to Pre-flight Checker →", use_container_width=True, type="primary"):
            st.session_state["page"] = "Pre-flight Checker"
            st.rerun()

    with col2:
        st.subheader("Step 2 — PAC Report")
        st.write(
            "Once your document has been exported as a PDF and all fixes are made, upload it here "
            "to generate a **PAC-style accessibility test report** you can save and share."
        )
        st.markdown("**Accepts:** `.pdf` only")
        if st.button("Go to PAC Report Generator →", use_container_width=True):
            st.session_state["page"] = "PAC Report Generator"
            st.rerun()

    st.divider()
    st.caption("Standard: ISO 14289-1 (PDF/UA) | Matterhorn Protocol 1.1 | Demo build — no login required")
