import streamlit as st
from src.checkers.pdf_checker import check_pdf
from src.checkers.docx_checker import check_docx
from src.checkers.pptx_checker import check_pptx
from src.reports.excel_export import build_excel
from src.db.database import save_report


ACCEPTED_TYPES = ["pdf", "docx", "pptx"]

STATUS_ICON  = {"pass": "✅", "fail": "❌", "na": "➖"}
STATUS_LABEL = {"pass": "Pass", "fail": "Fix Required", "na": "Not Applicable"}


def render():
    st.title("Pre-flight Accessibility Checker")
    st.write(
        "Upload your document below. The tool will check it against the Matterhorn Protocol "
        "and show you exactly what needs to be fixed."
    )

    uploaded = st.file_uploader(
        "Drop your file here or click to browse",
        type=ACCEPTED_TYPES,
        accept_multiple_files=False,
    )

    if uploaded is None:
        st.info("Waiting for a file. Accepted formats: .docx, .pptx, .pdf")
        return

    file_bytes = uploaded.read()
    ext = uploaded.name.rsplit(".", 1)[-1].lower()

    with st.spinner("Checking document for accessibility issues…"):
        if ext == "pdf":
            results = check_pdf(file_bytes, uploaded.name)
        elif ext == "docx":
            results = check_docx(file_bytes, uploaded.name)
        elif ext == "pptx":
            results = check_pptx(file_bytes, uploaded.name)
        else:
            st.error("Unsupported file type.")
            return

    save_report(uploaded.name, ext, results, check_type="preflight")

    # ── Summary bar ──────────────────────────────────────────────────────────
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    na     = sum(1 for r in results if r["status"] == "na")

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Passed", passed)
    col2.metric("Fix Required", failed, delta=f"-{failed}" if failed else None,
                delta_color="inverse" if failed else "off")
    col3.metric("Not Applicable", na)

    if failed == 0:
        st.success("No issues found. This document looks good to export as an accessible PDF.")
    else:
        st.warning(f"{failed} issue(s) need to be fixed before this document meets accessibility standards.")

    # ── Issue list ────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("Results by Checkpoint")

    show_all = st.checkbox("Show passed and not-applicable checks too", value=False)

    for result in results:
        status = result["status"]
        if not show_all and status != "fail":
            continue

        icon  = STATUS_ICON[status]
        label = STATUS_LABEL[status]
        colour = "🔴" if status == "fail" else ("🟢" if status == "pass" else "⚪")

        with st.expander(f"{icon} [{result['id']}] {result['group_name']} — **{label}**"):
            st.markdown(f"**What this means:** {result['plain_english']}")
            if status == "fail":
                st.markdown(f"**How to fix it:** {result['fix_hint']}")

    # ── Excel export ──────────────────────────────────────────────────────────
    st.divider()
    excel_bytes = build_excel(results, uploaded.name)
    st.download_button(
        label="Download Fix List as Excel (.xlsx)",
        data=excel_bytes,
        file_name=f"accessibility_fixes_{uploaded.name.rsplit('.', 1)[0]}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
