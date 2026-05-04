import streamlit as st
from src.checkers.pdf_checker import check_pdf
from src.reports.pac_report import build_pac_report
from src.db.database import save_report


def render():
    st.title("PAC Report Generator")
    st.write(
        "Upload your final PDF here to generate a PAC-style accessibility test report. "
        "This report can be downloaded and shared with your accessibility reviewer."
    )

    uploaded = st.file_uploader(
        "Drop your PDF here or click to browse",
        type=["pdf"],
        accept_multiple_files=False,
    )

    if uploaded is None:
        st.info("Waiting for a PDF file.")
        return

    file_bytes = uploaded.read()

    with st.spinner("Running full Matterhorn Protocol check…"):
        results = check_pdf(file_bytes, uploaded.name)

    save_report(uploaded.name, "pdf", results)

    # ── Summary ───────────────────────────────────────────────────────────────
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = sum(1 for r in results if r["status"] == "fail")
    na     = sum(1 for r in results if r["status"] == "na")

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Passed", passed)
    col2.metric("Failed", failed, delta=f"-{failed}" if failed else None,
                delta_color="inverse" if failed else "off")
    col3.metric("Not Applicable", na)

    if failed == 0:
        st.success("This PDF passes all checked Matterhorn Protocol criteria.")
    else:
        st.error(f"This PDF failed {failed} check(s). See the report for details.")

    # ── PAC PDF report download ───────────────────────────────────────────────
    st.divider()
    with st.spinner("Generating PAC-style PDF report…"):
        report_bytes = build_pac_report(results, uploaded.name)

    st.download_button(
        label="Download PAC Report (.pdf)",
        data=report_bytes,
        file_name=f"PAC_Report_{uploaded.name.rsplit('.', 1)[0]}.pdf",
        mime="application/pdf",
        type="primary",
    )

    # ── On-screen preview ─────────────────────────────────────────────────────
    st.divider()
    st.subheader("On-screen Results")
    for result in results:
        status = result["status"]
        icon = {"pass": "✅", "fail": "❌", "na": "➖"}[status]
        with st.expander(f"{icon} [{result['id']}] {result['group_name']} — {status.upper()}"):
            st.write(result["plain_english"])
            if status == "fail":
                st.markdown(f"**Fix:** {result['fix_hint']}")
