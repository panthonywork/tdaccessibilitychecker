import json
import streamlit as st
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "checkpoints.json"


@st.cache_data
def load_checkpoints() -> list[dict]:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["groups"]


def get_checkpoints_for_filetype(file_type: str) -> list[dict]:
    """Return flat list of checkpoints applicable to the given file type (pdf/docx/pptx)."""
    results = []
    for group in load_checkpoints():
        for cp in group["checkpoints"]:
            if file_type in cp.get("applies_to", []):
                results.append({**cp, "group_id": group["id"], "group_name": group["name"]})
    return results
