"""Mockable clients for GSTN integrations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


class GSTNIntegrationError(RuntimeError):
    """Raised when a GSTN API call fails."""


@dataclass
class GSTNClient:
    """A lightweight stub for NIC IRP and GST portal APIs.

    The implementation is intentionally simple so it can be replaced with a
    production ready HTTP client that performs authenticated calls to the
    official GSTN systems.
    """

    base_url: str
    auth_token: Optional[str] = None

    def is_authenticated(self) -> bool:
        return self.auth_token is not None

    def authenticate(self, client_id: str, client_secret: str) -> None:
        if not client_id or not client_secret:
            raise GSTNIntegrationError("Client credentials missing")
        self.auth_token = f"{client_id}:{client_secret}"

    def upload_return(self, form: str, payload: Dict[str, str]) -> str:
        if not self.is_authenticated():
            raise GSTNIntegrationError("Authentication required")
        if form not in {"GSTR1", "GSTR3B", "GSTR9"}:
            raise GSTNIntegrationError("Unsupported form type")
        if not payload:
            raise GSTNIntegrationError("No payload supplied")
        return f"ACK-{form}-{len(payload)}"

    def generate_irn(self, einvoice_payload: Dict[str, str]) -> str:
        if not self.is_authenticated():
            raise GSTNIntegrationError("Authentication required")
        if "Irn" not in einvoice_payload:
            raise GSTNIntegrationError("Invoice payload missing IRN seed")
        return einvoice_payload["Irn"]

    def fetch_gstr2b(self, gstin: str) -> Dict[str, str]:
        if not self.is_authenticated():
            raise GSTNIntegrationError("Authentication required")
        if not gstin:
            raise GSTNIntegrationError("GSTIN required")
        return {"gstin": gstin, "status": "stub", "invoices": []}
