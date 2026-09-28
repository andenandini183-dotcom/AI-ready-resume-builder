"""
Validation utilities for resume forms and data models.
Provides reusable validation functions returning (is_valid, error_message).
"""

import re
from typing import Tuple, Optional


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validates email format."""
    if not email or not email.strip():
        return True, None  # Optional field check handled separately if required
        
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email.strip()):
        return False, "Please enter a valid email address (e.g. john@example.com)."
    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """Validates phone number format."""
    if not phone or not phone.strip():
        return True, None
        
    cleaned = phone.strip()
    # Support international format, dashes, spaces, parentheses
    pattern = r"^\+?[0-9\s\-\(\)\.]{7,20}$"
    if not re.match(pattern, cleaned):
        return False, "Please enter a valid phone number (e.g. +1-555-0199)."
    return True, None


def validate_url(url: str, label: str = "URL") -> Tuple[bool, Optional[str]]:
    """Validates website / web profile URL format."""
    if not url or not url.strip():
        return True, None
        
    cleaned = url.strip()
    if not (cleaned.startswith("http://") or cleaned.startswith("https://") or cleaned.startswith("www.")):
        cleaned = "https://" + cleaned
        
    pattern = r"^(https?://)?([\w\d\-_]+\.)+[\w\d\-_]+(/[\w\d\-_./?%&=#]*)?$"
    if not re.match(pattern, cleaned, re.IGNORECASE):
        return False, f"Please enter a valid {label} (e.g. https://linkedin.com/in/username)."
    return True, None


def validate_required(value: str, field_name: str) -> Tuple[bool, Optional[str]]:
    """Validates that a required field is non-empty."""
    if not value or not value.strip():
        return False, f"{field_name} is required."
    return True, None


def validate_length(value: str, field_name: str, max_length: int) -> Tuple[bool, Optional[str]]:
    """Validates string character limit."""
    if value and len(value) > max_length:
        return False, f"{field_name} must not exceed {max_length} characters."
    return True, None


def validate_date_format(date_str: str, field_name: str = "Date") -> Tuple[bool, Optional[str]]:
    """Validates date format (YYYY-MM, YYYY, or Present)."""
    if not date_str or not date_str.strip():
        return True, None
        
    cleaned = date_str.strip()
    if cleaned.lower() in ["present", "current", "ongoing"]:
        return True, None
        
    pattern = r"^(\d{4})(- (0[1-9]|1[0-2]))?$"
    if not re.match(pattern, cleaned):
        return False, f"{field_name} must be in YYYY-MM, YYYY, or 'Present' format."
    return True, None
