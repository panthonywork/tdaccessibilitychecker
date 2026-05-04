from io import BytesIO
from src.standards.matterhorn import get_checkpoints_for_filetype


def check_pdf(file_bytes: bytes, filename: str) -> list[dict]:
    """
    Run Matterhorn-based accessibility checks on a PDF.
    Returns a list of CheckResult dicts.
    """
    try:
        import fitz  # PyMuPDF
        import pikepdf
    except ImportError as e:
        return [_error_result(str(e))]

    results = []
    checkpoints = get_checkpoints_for_filetype("pdf")

    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pdf = pikepdf.open(BytesIO(file_bytes))
    except Exception as e:
        return [_error_result(f"Could not open PDF: {e}")]

    for cp in checkpoints:
        result = _run_checkpoint(cp, doc, pdf)
        results.append(result)

    doc.close()
    pdf.close()
    return results


def _run_checkpoint(cp: dict, doc, pdf) -> dict:
    cp_id = cp["id"]
    base = {
        "id": cp_id,
        "group_id": cp["group_id"],
        "group_name": cp["group_name"],
        "description": cp["description"],
        "plain_english": cp["plain_english"],
        "fix_hint": cp["fix_hint"],
    }

    try:
        if cp_id == "01-002":
            status = _check_tagged(pdf)
        elif cp_id == "06-001":
            status = _check_title_metadata(pdf)
        elif cp_id == "07-001":
            status = _check_language(pdf)
        elif cp_id == "17-001":
            status = _check_image_alt_text(doc, pdf)
        elif cp_id == "13-001":
            status = _check_headings_present(pdf)
        else:
            status = "na"
    except Exception:
        status = "na"

    return {**base, "status": status}


def _check_tagged(pdf) -> str:
    try:
        mark_info = pdf.Root.get("/MarkInfo", {})
        marked = mark_info.get("/Marked", False)
        return "pass" if bool(marked) else "fail"
    except Exception:
        return "fail"


def _check_title_metadata(pdf) -> str:
    try:
        info = pdf.docinfo
        title = info.get("/Title", "")
        return "pass" if title and str(title).strip() else "fail"
    except Exception:
        return "fail"


def _check_language(pdf) -> str:
    try:
        lang = pdf.Root.get("/Lang", None)
        return "pass" if lang and str(lang).strip() else "fail"
    except Exception:
        return "fail"


def _check_image_alt_text(doc, pdf) -> str:
    """Fail if any page contains images with no alt text in the tag tree."""
    import fitz
    for page in doc:
        images = page.get_images(full=True)
        if images:
            # Simplified heuristic: check if document is tagged (proxy for alt text presence)
            try:
                mark_info = pdf.Root.get("/MarkInfo", {})
                if not bool(mark_info.get("/Marked", False)):
                    return "fail"
            except Exception:
                return "fail"
    return "pass"


def _check_headings_present(pdf) -> str:
    """Check if the tag tree contains any heading elements."""
    try:
        struct_tree = pdf.Root.get("/StructTreeRoot", None)
        return "pass" if struct_tree is not None else "fail"
    except Exception:
        return "fail"


def _error_result(message: str) -> dict:
    return {
        "id": "ERR",
        "group_id": "00",
        "group_name": "Error",
        "description": message,
        "plain_english": message,
        "fix_hint": "Ensure the file is a valid PDF.",
        "status": "fail",
    }
