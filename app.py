import streamlit as st

st.set_page_config(
    page_title="TD Accessibility Checker",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.pages import home, preflight, pac_checker, history

PAGES = {
    "Home": home,
    "Pre-flight Checker": preflight,
    "PAC Report Generator": pac_checker,
    "Report History": history,
}

with st.sidebar:
    st.title("TD Accessibility")
    st.caption("Document Accessibility Tool")
    st.divider()
    selection = st.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

PAGES[selection].render()
