from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional

from .constants import (
    STATE_CODES,
    UNION_TERRITORY_CODES,
    UNION_TERRITORY_WITH_LEGISLATURE,
)
from .gstin import validate_gstin

@dataclass
class Item:
    description: str
    hsn_code: str
    quantity: int
    price: float
    gst_rate: float  # e.g., 18 for 18%
    sac_code: Optional[str] = None

    @property
    def taxable_value(self) -> float:
        return self.quantity * self.price

    def to_dict(self) -> Dict[str, str]:
        return {
            "description": self.description,
            "hsn_code": self.hsn_code,
            "sac_code": self.sac_code or "",
            "quantity": str(self.quantity),
            "price": f"{self.price:.2f}",
            "gst_rate": f"{self.gst_rate:.2f}",
            "taxable_value": f"{self.taxable_value:.2f}",
        }

@dataclass
class Party:
    name: str
    gstin: str
    state_code: str
    email: Optional[str] = None
    phone: Optional[str] = None

    def __post_init__(self):
        if not validate_gstin(self.gstin):
            raise ValueError("Invalid GSTIN")
        if self.state_code != self.gstin[:2]:
            raise ValueError("State code mismatch with GSTIN")
        if self.state_code not in STATE_CODES:
            raise ValueError("Unknown state code")

@dataclass
class Invoice:
    seller: Party
    buyer: Party
    items: List[Item]
    invoice_number: str
    place_of_supply: str
    invoice_date: date = field(default_factory=date.today)
    cgst: float = 0.0
    sgst: float = 0.0
    igst: float = 0.0
    utgst: float = 0.0
    total: float = 0.0
    qr_data: Optional[str] = None
    taxable_total: float = 0.0
    line_breakup: List[Dict[str, float]] = field(default_factory=list)

    def calculate_taxes(self) -> None:
        """Calculate GST components for the invoice.

        Handles intra-state, inter-state and Union Territory flows by
        splitting the tax components appropriately and recording a per-line
        breakup for downstream accounting or GST return generation.
        """

        self.cgst = self.sgst = self.igst = self.utgst = 0.0
        self.line_breakup.clear()
        self.taxable_total = sum(i.taxable_value for i in self.items)

        intrastate = self.seller.state_code == self.place_of_supply
        is_ut = (
            self.place_of_supply in UNION_TERRITORY_CODES
            and self.place_of_supply not in UNION_TERRITORY_WITH_LEGISLATURE
        )

        for item in self.items:
            tax = item.taxable_value * item.gst_rate / 100
            line_components = {"taxable_value": item.taxable_value}

            if intrastate:
                if is_ut:
                    half = tax / 2
                    self.cgst += half
                    self.utgst += half
                    line_components.update({"cgst": half, "utgst": half})
                else:
                    half = tax / 2
                    self.cgst += half
                    self.sgst += half
                    line_components.update({"cgst": half, "sgst": half})
            else:
                self.igst += tax
                line_components.update({"igst": tax})

            self.line_breakup.append(line_components)

        self.total = (
            self.taxable_total + self.cgst + self.sgst + self.igst + self.utgst
        )

    def to_einvoice_payload(self) -> Dict[str, str]:
        """Create a dictionary that resembles an e-invoice payload."""

        self.calculate_taxes()
        items_payload = [item.to_dict() for item in self.items]
        data = {
            "Version": "1.1",
            "TranDtls": {
                "TaxSch": "GST",
                "SupTyp": "B2B" if self.buyer.gstin else "B2C",
            },
            "DocDtls": {
                "Typ": "INV",
                "No": self.invoice_number,
                "Dt": self.invoice_date.strftime("%d/%m/%Y"),
            },
            "SellerDtls": {
                "Gstin": self.seller.gstin,
                "LglNm": self.seller.name,
                "Stcd": self.seller.state_code,
                "Ph": self.seller.phone,
                "Em": self.seller.email,
            },
            "BuyerDtls": {
                "Gstin": self.buyer.gstin,
                "LglNm": self.buyer.name,
                "Stcd": self.buyer.state_code,
                "Ph": self.buyer.phone,
                "Em": self.buyer.email,
            },
            "ItemList": items_payload,
            "ValDtls": {
                "AssVal": round(self.taxable_total, 2),
                "CgstVal": round(self.cgst, 2),
                "SgstVal": round(self.sgst, 2),
                "IgstVal": round(self.igst, 2),
                "UtgstVal": round(self.utgst, 2),
                "TotInvVal": round(self.total, 2),
            },
        }

        irn_seed = json.dumps(data, sort_keys=True).encode()
        irn = hashlib.sha256(irn_seed).hexdigest()
        data["Irn"] = irn
        self.qr_data = irn
        return data


@dataclass
class RecurringInvoiceTemplate:
    """A simplified recurring invoice definition for SaaS billing."""

    template_name: str
    seller: Party
    buyer: Party
    items: List[Item]
    billing_cycle_days: int
    next_invoice_date: date
    is_active: bool = True

    def generate_invoice(self, invoice_number: str) -> Invoice:
        invoice = Invoice(
            seller=self.seller,
            buyer=self.buyer,
            items=self.items,
            invoice_number=invoice_number,
            place_of_supply=self.seller.state_code,
            invoice_date=self.next_invoice_date,
        )
        invoice.calculate_taxes()
        return invoice

    def advance_cycle(self) -> None:
        if not self.is_active:
            raise RuntimeError("Template is deactivated")
        self.next_invoice_date = self.next_invoice_date.fromordinal(
            self.next_invoice_date.toordinal() + self.billing_cycle_days
        )


@dataclass
class AdjustmentNote:
    """Represents a debit or credit note."""

    reference_invoice: Invoice
    note_number: str
    amount: float
    reason: str
    is_credit: bool

    def ledger_impact(self) -> Dict[str, float]:
        if self.amount <= 0:
            raise ValueError("Amount should be positive for notes")
        return {
            "debit": self.amount if self.is_credit else 0.0,
            "credit": 0.0 if self.is_credit else self.amount,
        }
