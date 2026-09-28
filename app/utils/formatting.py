import re
from typing import List, Union


def clean_garbage_text(text: str) -> str:
    """Cleans up garbled text, residual ATS noise terms, PDF extraction artifacts, and double bullet symbols."""
    if not text:
        return ""
    text = re.sub(r"^\s*[*\-•–>\.]+\s*", "", text).strip()
    text = re.sub(r"\(Tech:\s*([^)]+)\)", r"\1", text)
    text = re.sub(r"Tech:\s*Align,\s*Applications\.strong", "", text, flags=re.IGNORECASE)
    text = re.sub(r",?\s*Align,\s*Applications\.strong", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\|\s*Tech:\s*", " | ", text)
    text = re.sub(r"\bT\s+ech:\s*", "Tech: ", text)
    text = re.sub(r"\bT\s+op\b", "Top", text)
    text = re.sub(r"\bT\s+echnology\b", "Technology", text)
    text = re.sub(r"\bF\s+ull\b", "Full", text)
    text = re.sub(r"\bf\s+rontend\b", "frontend", text, flags=re.IGNORECASE)
    text = re.sub(r"\bT\s+ech\b", "Tech", text)
    text = re.sub(r"•\s*•", "•", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def format_date_range(start_date: str, end_date: str, is_current: bool = False) -> str:
    """Formats start and end dates into a clean display range string."""
    start = start_date.strip() if start_date else ""
    if is_current:
        end = "Present"
    else:
        end = end_date.strip() if end_date else ""
        
    if start and end:
        return f"{start} – {end}"
    elif start:
        return start
    elif end:
        return end
    return ""


def parse_bullet_list(text: Union[str, List[str]]) -> List[str]:
    """Converts multi-line text or raw string into clean list of bullet strings."""
    if isinstance(text, list):
        return [clean_garbage_text(b) for b in text if b and clean_garbage_text(b)]
        
    if not text or not text.strip():
        return []
        
    lines = text.strip().split("\n")
    bullets = []
    for line in lines:
        cleaned = line.strip()
        cleaned = re_strip_bullet_prefix(cleaned)
        cleaned = clean_garbage_text(cleaned)
        if cleaned:
            bullets.append(cleaned)
    return bullets


def re_strip_bullet_prefix(text: str) -> str:
    """Strips all common leading bullet characters (*, -, •, –, >, .)."""
    if not text:
        return ""
    text = text.strip()
    while text and (text[0] in ["*", "-", "•", "–", ">", "."] or text.startswith(("•", "-", "*", "–", ">"))):
        text = re.sub(r"^[*\-•–>\.\s]+", "", text).strip()
    return text


def format_contact_info(location: str, email: str, phone: str, linkedin: str = "", github: str = "") -> str:
    """Formats contact details into a pipe-separated string."""
    parts = [clean_garbage_text(p) for p in [location, phone, email, linkedin, github] if p and p.strip()]
    return " | ".join(parts)

