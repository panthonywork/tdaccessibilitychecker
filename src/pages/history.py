import streamlit as st
from src.db.database import get_reports_by_type, get_report_by_id
from src.reports.excel_export import build_excel
from src.reports.pac_report import build_pac_report

FILE_TYPE_LABEL = {"pdf": "PDF", "docx": "Word", "pptx": "PowerPoint"}


def _status_icon(failed: int) -> str:
    return "🟢" if failed == 0 else "🔴"


def _render_preflight_tab():
    reports = get_reports_by_type("preflight")

    if not reports:
        st.info("No pre-flight checks yet. Upload a document in the Pre-flight Checker to get started.")
        return

    st.caption(f"{len(reports)} document(s) checked")

    for report in reports:
        icon = _status_icon(report["failed"])
        file_label = FILE_TYPE_LABEL.get(report["file_type"], report["file_type"].upper())
        date = report["checked_at"][:10]
        total = report["total_checks"] or 1

        with st.expander(
            f"{icon}  {report['filename']}  ·  {file_label}  ·  {date}  "
            f"·  {report['passed']}/{total} passed"
        ):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Passed", report["passed"])
            col2.metric("Fix Required", report["failed"])
            col3.metric("N/A", report["not_applicable"])
            col4.metric("File type", file_label)

            full = get_report_by_id(report["id"])
            if full:
                # Show failed items inline
                failures = [r for r in full["results"] if r["status"] == "fail"]
                if failures:
                    st.markdown("**Issues found:**")
                    for f in failures:
                        st.markdown(f"- ❌ **[{f['id']}]** {f['plain_english']}")
                else:
                    st.success("No issues found — this document passed all checks.")

                st.divider()
                excel_bytes = build_excel(full["results"], report["filename"])
                st.download_button(
                    label="Download Fix List (.xlsx)",
                    data=excel_bytes,
                    file_name=f"preflight_{report['filename'].rsplit('.', 1)[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"xl_{report['id']}",
                )


def _render_pac_tab():
    reports = get_reports_by_type("pac")

    if not reports:
        st.info("No PAC reports yet. Upload a PDF in the PAC Report Generator to get started.")
        return

    st.caption(f"{len(reports)} report(s) generated")

    for report in reports:
        icon = _status_icon(report["failed"])
        date = report["checked_at"][:10]
        total = report["total_checks"] or 1
        verdict = "PASS" if report["failed"] == 0 else f"{report['failed']} FAILED"

        with st.expander(
            f"{icon}  {report['filename']}  ·  {date}  ·  {verdict}"
        ):
            col1, col2, col3 = st.columns(3)
            col1.metric("Passed", report["passed"])
            col2.metric("Failed", report["failed"])
            col3.metric("N/A", report["not_applicable"])

            full = get_report_by_id(report["id"])
            if full:
                failures = [r for r in full["results"] if r["status"] == "fail"]
                if failures:
                    st.markdown("**Failed checkpoints:**")
                    for f in failures:
                        st.markdown(f"- ❌ **[{f['id']}]** {f['plain_english']}")
                else:
                    st.success("All checked criteria passed.")

                st.divider()
                col_a, col_b = st.columns(2)

                with col_a:
                    pac_bytes = build_pac_report(full["results"], report["filename"])
                    st.download_button(
                        label="Download PAC Report (.pdf)",
                        data=pac_bytes,
                        file_name=f"PAC_Report_{report['filename'].rsplit('.', 1)[0]}.pdf",
                        mime="application/pdf",
                        key=f"pac_{report['id']}",
                        type="primary",
                    )

                with col_b:
                    excel_bytes = build_excel(full["results"], report["filename"])
                    st.download_button(
                        label="Download as Excel (.xlsx)",
                        data=excel_bytes,
                        file_name=f"PAC_{report['filename'].rsplit('.', 1)[0]}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"xl_{report['id']}",
                    )


def render():
    st.title("Report History")
    st.write("All past checks are saved here. Uploaded files are never stored — only the results.")

    tab1, tab2 = st.tabs(["Pre-Flight Documents", "PAC Reports"])

    with tab1:
        _render_preflight_tab()

    with tab2:
        _render_pac_tab()
