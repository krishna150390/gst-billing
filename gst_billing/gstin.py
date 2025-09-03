import re
from .constants import STATE_CODES

GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{3}$")

def validate_gstin(gstin: str) -> bool:
    """Validate GSTIN format and state code."""
    if not GSTIN_REGEX.match(gstin):
        return False
    state_code = gstin[:2]
    return state_code in STATE_CODES
