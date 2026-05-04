# TD Accessibility Document Checker

A Streamlit web app that checks Word, PowerPoint, and PDF files for accessibility compliance against ISO 14289-1 (PDF/UA) using the Matterhorn Protocol. Produces on-screen fix lists, Excel exports, and a PAC-style PDF report.

## Tech Stack

- **UI + App logic**: Streamlit (Python 3.11+)
- **PDF inspection**: PyMuPDF (`fitz`) + `pikepdf`
- **Word files**: `python-docx`
- **PowerPoint files**: `python-pptx`
- **Report generation**: `ReportLab`
- **Excel export**: `openpyxl`
- **Database**: SQLite via `sqlite3` (stdlib)

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
app.py                   # Streamlit entry point — page routing only
src/
  checkers/
    pdf_checker.py       # PDF tag tree + Matterhorn checkpoint logic
    docx_checker.py      # Word document accessibility checks
    pptx_checker.py      # PowerPoint accessibility checks
  reports/
    pac_report.py        # Generates PAC-2024-style PDF report via ReportLab
    excel_export.py      # Writes issue list to .xlsx
  pages/
    home.py              # Landing page
    preflight.py         # Module 1: pre-flight checker UI
    pac_checker.py       # Module 2: PAC report generator UI
    history.py           # Report history table
  db/
    database.py          # SQLite read/write for report history
  standards/
    matterhorn.py        # Loads and exposes checkpoint definitions
config/
  checkpoints.json       # All 31 Matterhorn Protocol checkpoint groups + rules
assets/                  # Logos and static images for report branding
```

## Code Conventions

- All checker functions return a list of `CheckResult` dicts: `{id, group, status, message, fix_hint}`
- `status` values: `"pass"`, `"fail"`, `"na"` (not applicable)
- Uploaded files are **never written to disk** — use `BytesIO` throughout
- Uploaded files are deleted from memory immediately after checking; only the results dict is kept
- Page modules expose a single `render()` function called by `app.py`
- Use `st.cache_data` for functions that parse static config files (checkpoints.json)

## Accessibility Standards

This tool implements the [Matterhorn Protocol](https://pdfa.org/resource/the-matterhorn-protocol/) (31 checkpoint groups) against [ISO 14289-1 (PDF/UA)](https://pdfa.org/resource/iso-14289-pdfua/). TD Bank-specific standards will be layered on top in a future phase — leave extensibility hooks in `src/standards/`.

## Key Workflows

- **Add a new checkpoint**: add entry to `config/checkpoints.json`, implement detection logic in the relevant checker, add plain-English `fix_hint`
- **Style the PAC report**: all layout constants (colours, fonts, margins) are in `src/reports/pac_report.py` at the top of the file
- **Deploy to Streamlit Cloud**: push to GitHub, connect repo at share.streamlit.io, set Python 3.11

## What to Avoid

- Do not use `st.session_state` to store file contents — keep files in local function scope only
- Do not write uploaded files to the filesystem at any point
- Do not add login/auth logic — this is a no-auth demo build
- Do not add TD-specific branding or internal standards without the user confirming access to those materials
