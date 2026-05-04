import streamlit as st
from src.db.database import get_all_reports, get_report_by_id
from src.reports.excel_export import build_excel


def render():
    st.title("Report History")
    st.write("All past accessibility checks are listed below. Reports are kept; uploaded files are never stored.")

    reports = get_all_reports()

    if not reports:
        st.info("No reports yet. Run a check from the Pre-flight Checker or PAC Report Generator.")
        return

    for report in reports:
        total = report["total_checks"] or 1
        pass_pct = round(report["passed"] / total * 100)
        colour = "🟢" if report["failed"] == 0 else "🔴"

        with st.expander(
            f"{colour} {report['filename']}  |  {report['checked_at'][:10]}  |  "
            f"{report['passed']}/{total} passed"
        ):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Passed", report["passed"])
            col2.metric("Failed", report["failed"])
            col3.metric("N/A", report["not_applicable"])
            col4.metric("File type", report["file_type"].upper())

            full = get_report_by_id(report["id"])
            if full:
                excel_bytes = build_excel(full["results"], report["filename"])
                st.download_button(
                    label="Re-download Excel Fix List",
                    data=excel_bytes,
                    file_name=f"accessibility_fixes_{report['filename'].rsplit('.', 1)[0]}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_{report['id']}",
                )
