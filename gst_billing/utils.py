import json
from typing import Any

try:
    import qrcode
except ImportError:  # pragma: no cover - optional dependency
    qrcode = None


def generate_qr(data: Any, filename: str) -> None:
    """Generate a QR code from data and save as filename."""
    if qrcode is None:
        raise RuntimeError("qrcode package not installed")
    img = qrcode.make(json.dumps(data))
    img.save(filename)
