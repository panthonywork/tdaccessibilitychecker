"""
PAC-2024-style accessibility report using ReportLab Platypus.
Matches the layout of the official PAC Test Report image.
"""
from io import BytesIO
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER

# ── Colour palette ──────────────────────────────────────────────────────────
C_ORANGE   = colors.HexColor("#E8472A")
C_NAVY     = colors.HexColor("#1A1A2E")
C_GREEN    = colors.HexColor("#27AE60")
C_GREEN_BG = colors.HexColor("#EDF7F1")
C_RED      = colors.HexColor("#E74C3C")
C_RED_BG   = colors.HexColor("#FDEAEA")
C_GREY_BG  = colors.HexColor("#F5F5F5")
C_LINE     = colors.HexColor("#DDDDDD")
C_MID      = colors.HexColor("#666666")
C_BLACK    = colors.HexColor("#1A1A1A")
C_WHITE    = colors.white

PAGE_W, PAGE_H = A4
ML = 20 * mm   # left/right margin
MT = 20 * mm   # top/bottom margin
IW = PAGE_W - 2 * ML   # inner content width

# ── Checkpoint → PAC group mapping ─────────────────────────────────────────
GROUPS = {
    "Basic Requirements": {
        "ids": ["01", "07", "20"],
        "labels": {"01": "PDF Syntax / Structure", "07": "Natural Language", "20": "Colour and Contrast"},
    },
    "Logical Structure": {
        "ids": ["02", "13", "14", "15", "17", "28"],
        "labels": {
            "02": "Page Header", "13": "Headings", "14": "Tables",
            "15": "Lists", "17": "Alternative Descriptions", "28": "Links and Navigation",
        },
    },
    "Metadata and Settings": {
        "ids": ["06"],
        "labels": {"06": "Document Title / Metadata"},
    },
}

# ── Styles ──────────────────────────────────────────────────────────────────
def _styles():
    def s(name, **kw):
        return ParagraphStyle(name, **kw)

    return {
        "report_title": s("rt", fontSize=20, fontName="Helvetica-Bold", textColor=C_NAVY, spaceAfter=0),
        "pac_logo":     s("pl", fontSize=52, fontName="Helvetica-Bold", textColor=C_NAVY, alignment=TA_RIGHT, spaceAfter=0),
        "section_hdr":  s("sh", fontSize=10, fontName="Helvetica-Bold", textColor=C_NAVY, spaceBefore=6, spaceAfter=2),
        "field_label":  s("fl", fontSize=8,  fontName="Helvetica-Bold", textColor=C_NAVY, spaceAfter=1),
        "field_value":  s("fv", fontSize=9,  fontName="Helvetica",      textColor=C_BLACK, spaceAfter=4),
        "result_text":  s("rx", fontSize=10, fontName="Helvetica-Bold", textColor=C_NAVY, leading=14),
        "col_hdr":      s("ch", fontSize=8,  fontName="Helvetica-Bold", textColor=C_NAVY, alignment=TA_CENTER),
        "col_hdr_l":    s("cl", fontSize=8,  fontName="Helvetica-Bold", textColor=C_NAVY),
        "group_name":   s("gn", fontSize=9,  fontName="Helvetica-Bold", textColor=C_NAVY),
        "row_label":    s("rl", fontSize=8,  fontName="Helvetica",      textColor=C_BLACK),
        "row_num":      s("rn", fontSize=8,  fontName="Helvetica",      textColor=C_BLACK, alignment=TA_CENTER),
        "footer":       s("ft", fontSize=7,  fontName="Helvetica",      textColor=C_MID,   leading=10),
        "about_val":    s("av", fontSize=8,  fontName="Helvetica",      textColor=C_BLACK, spaceAfter=2),
    }


# ── PDF metadata extraction ─────────────────────────────────────────────────
def _extract_meta(pdf_bytes: bytes, filename: str) -> dict:
    meta = {
        "title": filename,
        "filename": filename,
        "language": "—",
        "tags": "—",
        "pages": "—",
        "size": f"{len(pdf_bytes) // 1024} KB",
        "thumbnail": None,
    }
    try:
        import fitz
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        meta["pages"] = str(doc.page_count)
        info = doc.metadata or {}
        if info.get("title"):
            meta["title"] = info["title"]
        if info.get("language"):
            meta["language"] = info["language"]
        # Render first page thumbnail at ~30% scale
        page = doc[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(0.4, 0.4))
        meta["thumbnail"] = BytesIO(pix.tobytes("png"))
        doc.close()
    except Exception:
        pass
    try:
        import pikepdf
        pdf = pikepdf.open(BytesIO(pdf_bytes))
        lang = pdf.Root.get("/Lang", None)
        if lang:
            meta["language"] = str(lang)
        st = pdf.Root.get("/StructTreeRoot", None)
        if st is not None:
            meta["tags"] = "Tagged"
        else:
            meta["tags"] = "Not tagged"
        pdf.close()
    except Exception:
        pass
    return meta


# ── Flowable builders ───────────────────────────────────────────────────────
def _header_table(st):
    data = [[
        Paragraph("PAC Test Report", st["report_title"]),
        Paragraph("PAC", st["pac_logo"]),
    ]]
    t = Table(data, colWidths=[IW * 0.6, IW * 0.4])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _section_heading(label: str, st) -> list:
    return [
        Paragraph(label, st["section_hdr"]),
        HRFlowable(width=IW, thickness=2, color=C_ORANGE, spaceAfter=8),
    ]


def _document_section(meta: dict, st) -> list:
    items = _section_heading("DOCUMENT", st)

    # Build metadata right column
    def field(label, value):
        return [
            Paragraph(label, st["field_label"]),
            HRFlowable(width="100%", thickness=0.75, color=C_ORANGE, spaceAfter=2),
            Paragraph(value or "—", st["field_value"]),
        ]

    meta_col = []
    for f in field("Title", meta["title"]):
        meta_col.append(f)
    for f in field("Filename", meta["filename"]):
        meta_col.append(f)

    # Language / Tags / Pages / Size row
    lw = (IW - 45 * mm) / 4   # divide right column into 4
    sub_data = [[
        Paragraph("Language", st["field_label"]),
        Paragraph("Tags", st["field_label"]),
        Paragraph("Pages", st["field_label"]),
        Paragraph("Size", st["field_label"]),
    ], [
        HRFlowable(width="100%", thickness=0.75, color=C_ORANGE),
        HRFlowable(width="100%", thickness=0.75, color=C_ORANGE),
        HRFlowable(width="100%", thickness=0.75, color=C_ORANGE),
        HRFlowable(width="100%", thickness=0.75, color=C_ORANGE),
    ], [
        Paragraph(meta["language"], st["field_value"]),
        Paragraph(meta["tags"], st["field_value"]),
        Paragraph(meta["pages"], st["field_value"]),
        Paragraph(meta["size"], st["field_value"]),
    ]]
    sub_t = Table(sub_data, colWidths=[lw] * 4)
    sub_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    meta_col.append(sub_t)

    # Thumbnail or placeholder
    THUMB_W = 40 * mm
    THUMB_H = 50 * mm
    if meta["thumbnail"]:
        try:
            thumb = Image(meta["thumbnail"], width=THUMB_W, height=THUMB_H, kind="proportional")
        except Exception:
            thumb = _placeholder_box(THUMB_W, THUMB_H)
    else:
        thumb = _placeholder_box(THUMB_W, THUMB_H)

    # 2-column layout: thumbnail | metadata
    doc_data = [[thumb, meta_col]]
    doc_t = Table(doc_data, colWidths=[45 * mm, IW - 45 * mm])
    doc_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("BOX", (0, 0), (0, 0), 0.5, C_LINE),
        ("BACKGROUND", (0, 0), (0, 0), C_GREY_BG),
        ("RIGHTPADDING", (0, 0), (0, 0), 4),
        ("LEFTPADDING", (1, 0), (1, 0), 10),
    ]))
    items.append(doc_t)
    items.append(Spacer(1, 8 * mm))
    return items


def _placeholder_box(w, h):
    """Simple grey placeholder when no thumbnail is available."""
    data = [[Paragraph("<br/>PDF<br/>Preview<br/>N/A", ParagraphStyle(
        "ph", fontSize=7, textColor=C_MID, alignment=TA_CENTER
    ))]]
    t = Table(data, colWidths=[w], rowHeights=[h])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_GREY_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _result_section(results: list[dict], st) -> list:
    items = _section_heading("RESULT", st)

    failed = sum(1 for r in results if r["status"] == "fail")
    passed = sum(1 for r in results if r["status"] == "pass")

    if failed == 0:
        banner_bg = C_GREEN_BG
        icon = "✔"
        icon_color = C_GREEN
        msg = "The PDF/UA requirements checked are fulfilled."
    else:
        banner_bg = C_RED_BG
        icon = "✘"
        icon_color = C_RED
        msg = f"The PDF/UA requirements are NOT fulfilled. {failed} check(s) failed."

    icon_style = ParagraphStyle("icon", fontSize=18, fontName="Helvetica-Bold",
                                 textColor=icon_color, alignment=TA_CENTER)
    banner_data = [[
        Paragraph(icon, icon_style),
        Paragraph(msg, st["result_text"]),
    ]]
    banner_t = Table(banner_data, colWidths=[14 * mm, IW - 14 * mm])
    banner_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), banner_bg),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (0, 0), 8),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("ROUNDEDCORNERS", [4, 4, 4, 4]),
    ]))
    items.append(banner_t)
    items.append(Spacer(1, 5 * mm))

    # Date / Standard row
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    dt_data = [[
        [Paragraph("Date/Time", st["field_label"]),
         HRFlowable(width="100%", thickness=0.5, color=C_LINE, spaceAfter=2),
         Paragraph(now, st["field_value"])],
        [Paragraph("Standard", st["field_label"]),
         HRFlowable(width="100%", thickness=0.5, color=C_LINE, spaceAfter=2),
         Paragraph("PDF/UA-1", st["field_value"])],
    ]]
    dt_t = Table(dt_data, colWidths=[IW / 2, IW / 2])
    dt_t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    items.append(dt_t)
    items.append(Spacer(1, 5 * mm))

    # Checkpoint table
    items.append(_checkpoint_table(results, st))
    items.append(Spacer(1, 8 * mm))
    return items


def _checkpoint_table(results: list[dict], st) -> Table:
    COL_W = [IW - 90 * mm, 30 * mm, 30 * mm, 30 * mm]

    # Header row
    rows = [[
        Paragraph("CHECKPOINT",  st["col_hdr_l"]),
        Paragraph("PASSED",      st["col_hdr"]),
        Paragraph("WARNED",      st["col_hdr"]),
        Paragraph("FAILED",      st["col_hdr"]),
    ]]
    style_cmds = [
        ("BACKGROUND",    (0, 0), (-1, 0),  C_GREY_BG),
        ("LINEBELOW",     (0, 0), (-1, 0),  1, C_LINE),
        ("TOPPADDING",    (0, 0), (-1, 0),  5),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  5),
        ("LEFTPADDING",   (0, 0), (0, -1),  4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",         (1, 0), (-1, -1), "CENTER"),
    ]

    # Build a fast lookup: group_id → {pass, warn, fail}
    by_group: dict = {}
    for r in results:
        gid = r.get("group_id", "")
        if gid not in by_group:
            by_group[gid] = {"pass": 0, "warn": 0, "fail": 0}
        s = r.get("status", "na")
        if s == "pass":
            by_group[gid]["pass"] += 1
        elif s == "fail":
            by_group[gid]["fail"] += 1

    row_idx = 1
    for group_name, group_info in GROUPS.items():
        # Group header row
        rows.append([
            Paragraph(group_name, st["group_name"]),
            "", "", "",
        ])
        style_cmds += [
            ("SPAN",          (0, row_idx), (-1, row_idx)),
            ("TOPPADDING",    (0, row_idx), (-1, row_idx), 6),
            ("BOTTOMPADDING", (0, row_idx), (-1, row_idx), 3),
            ("LINEABOVE",     (0, row_idx), (-1, row_idx), 0.5, C_LINE),
        ]
        row_idx += 1

        # Sub-rows
        for gid, label in group_info["labels"].items():
            counts = by_group.get(gid, {"pass": 0, "warn": 0, "fail": 0})
            rows.append([
                Paragraph(label, st["row_label"]),
                Paragraph(str(counts["pass"]), st["row_num"]),
                Paragraph(str(counts["warn"]), st["row_num"]),
                Paragraph(str(counts["fail"]), st["row_num"]),
            ])
            style_cmds += [
                ("LINEBELOW",     (0, row_idx), (-1, row_idx), 0.5, C_LINE),
                ("TOPPADDING",    (0, row_idx), (-1, row_idx), 4),
                ("BOTTOMPADDING", (0, row_idx), (-1, row_idx), 4),
            ]
            if counts["fail"] > 0:
                style_cmds.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), C_RED))
                style_cmds.append(("FONTNAME",  (3, row_idx), (3, row_idx), "Helvetica-Bold"))
            row_idx += 1

    t = Table(rows, colWidths=COL_W, repeatRows=1)
    t.setStyle(TableStyle(style_cmds))
    return t


def _about_section(st) -> list:
    items = _section_heading("ABOUT THIS REPORT", st)
    data = [
        [Paragraph("Generated by", st["field_label"]), Paragraph("TD Accessibility Checker", st["about_val"])],
        [Paragraph("Standard",     st["field_label"]), Paragraph("ISO 14289-1 (PDF/UA) / Matterhorn Protocol 1.1", st["about_val"])],
        [Paragraph("Date",         st["field_label"]), Paragraph(datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"), st["about_val"])],
    ]
    for row in data:
        items.append(Table([row], colWidths=[45 * mm, IW - 45 * mm], style=TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("TOPPADDING",    (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ("LINEBELOW",     (0, 0), (-1, -1), 0.5, C_LINE),
        ])))
    items.append(Spacer(1, 6 * mm))
    return items


def _footer_paragraph(st) -> list:
    return [
        HRFlowable(width=IW, thickness=0.5, color=C_LINE, spaceBefore=4, spaceAfter=4),
        Paragraph(
            "This report evaluates document accessibility for machine-checkable criteria according to "
            "ISO 14289-1 (PDF/UA) using the Matterhorn Protocol. "
            "Generated by TD Accessibility Checker — Demo Build.",
            st["footer"]
        ),
    ]


# ── Public API ──────────────────────────────────────────────────────────────
def build_pac_report(results: list[dict], filename: str, pdf_bytes: bytes = None) -> bytes:
    buffer = BytesIO()
    st = _styles()

    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=ML, rightMargin=ML,
        topMargin=MT, bottomMargin=MT,
    )
    frame = Frame(ML, MT, IW, PAGE_H - 2 * MT, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])

    if pdf_bytes:
        meta = _extract_meta(pdf_bytes, filename)
    else:
        meta = {
            "title": filename, "filename": filename,
            "language": "—", "tags": "—", "pages": "—",
            "size": "—", "thumbnail": None,
        }

    story = []
    story.append(_header_table(st))
    story.append(HRFlowable(width=IW, thickness=0.5, color=C_LINE, spaceBefore=4, spaceAfter=8))
    story += _document_section(meta, st)
    story += _result_section(results, st)
    story += _about_section(st)
    story += _footer_paragraph(st)

    doc.build(story)
    return buffer.getvalue()
