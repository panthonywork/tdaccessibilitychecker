import streamlit as st

st.set_page_config(
    page_title="TD Accessibility Checker",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _check_password() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.title("TD Accessibility Checker")
    st.markdown("Please enter the password to continue.")
    pwd = st.text_input("Password", type="password", key="pwd_input")

    if st.button("Login", type="primary"):
        if pwd == st.secrets.get("APP_PASSWORD", ""):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Incorrect password. Please try again.")

    return False


if not _check_password():
    st.stop()

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
