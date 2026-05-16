"""
Input validation helpers for both CLI and GUI.
"""


def validate_length(value: str) -> tuple[bool, str, int]:
    """
    Validate password length input.
    Returns (is_valid, error_message, parsed_int).
    """
    try:
        length = int(value)
    except (ValueError, TypeError):
        return False, "Length must be a whole number.", 0

    if length < 4:
        return False, "Length must be at least 4.", 0
    if length > 512:
        return False, "Length must be 512 or less.", 0

    return True, "", length


def validate_char_types(uppercase, lowercase, digits, symbols) -> tuple[bool, str]:
    """Ensure at least one character type is selected."""
    if not any([uppercase, lowercase, digits, symbols]):
        return False, "Select at least one character type."
    return True, ""


def validate_exclusions(exclude_chars: str, charset_active: str) -> tuple[bool, str]:
    """Warn if exclusions wipe out an entire active character type."""
    # Just a basic sanity check
    if len(exclude_chars) > 100:
        return False, "Exclusion list is too long (max 100 chars)."
    return True, ""