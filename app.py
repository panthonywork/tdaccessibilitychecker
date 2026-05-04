import streamlit as st

st.set_page_config(
    page_title="TD Accessibility Checker",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* ── Sidebar ─────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background-color: #006B3F;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #FFFFFF !important;
        font-size: 0.95rem;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.3);
    }
    /* Active nav item */
    [data-testid="stSidebar"] [data-baseweb="radio"] div[aria-checked="true"] {
        background-color: rgba(255,255,255,0.15);
        border-radius: 6px;
    }

    /* ── Top header bar ──────────────────────────────────── */
    [data-testid="stHeader"] {
        background-color: #006B3F;
    }

    /* ── Primary buttons → TD Green ─────────────────────── */
    .stButton > button[kind="primary"] {
        background-color: #00A550;
        border: none;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 4px;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #006B3F;
        color: #FFFFFF;
    }

    /* ── Secondary buttons ───────────────────────────────── */
    .stButton > button[kind="secondary"] {
        border: 2px solid #00A550;
        color: #00A550;
        border-radius: 4px;
        font-weight: 600;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #00A550;
        color: #FFFFFF;
    }

    /* ── Download buttons ────────────────────────────────── */
    [data-testid="stDownloadButton"] button {
        background-color: #00A550;
        color: #FFFFFF;
        border: none;
        border-radius: 4px;
        font-weight: 600;
    }
    [data-testid="stDownloadButton"] button:hover {
        background-color: #006B3F;
    }

    /* ── Page titles ─────────────────────────────────────── */
    h1 {
        color: #006B3F !important;
        font-weight: 700;
    }
    h2, h3 {
        color: #1A1A1A !important;
    }

    /* ── Metric cards ────────────────────────────────────── */
    [data-testid="stMetric"] {
        background-color: #F4F4F4;
        border-left: 4px solid #00A550;
        border-radius: 4px;
        padding: 0.5rem 1rem;
    }

    /* ── File uploader ───────────────────────────────────── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #00A550;
        border-radius: 6px;
        background-color: #F9FFF9;
    }

    /* ── Success / error / info banners ──────────────────── */
    [data-testid="stAlert"][data-baseweb="notification"][kind="info"] {
        border-left: 4px solid #00A550;
    }
</style>
""", unsafe_allow_html=True)


def _check_password() -> bool:
    if st.session_state.get("authenticated"):
        return True

    st.markdown("""
        <div style="text-align:center; padding: 2rem 0 1rem;">
            <span style="font-size:2.2rem; font-weight:700; color:#006B3F;">TD Accessibility Checker</span><br>
            <span style="color:#54565A;">Please enter the password to continue.</span>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd = st.text_input("Password", type="password", key="pwd_input", label_visibility="collapsed",
                            placeholder="Enter password")
        if st.button("Login", type="primary", use_container_width=True):
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

PAGE_NAMES = list(PAGES.keys())

if "page_index" not in st.session_state:
    st.session_state["page_index"] = 0

with st.sidebar:
    st.markdown("""
        <div style="padding: 0.5rem 0 0.25rem;">
            <span style="font-size:1.2rem; font-weight:700; letter-spacing:0.5px;">TD Accessibility</span><br>
            <span style="font-size:0.78rem; opacity:0.8;">Document Accessibility Tool</span>
        </div>
    """, unsafe_allow_html=True)
    st.divider()
    selection = st.radio(
        "Navigate", PAGE_NAMES,
        index=st.session_state["page_index"],
        label_visibility="collapsed",
    )
    st.session_state["page_index"] = PAGE_NAMES.index(selection)

PAGES[selection].render()
