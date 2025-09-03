from dataclasses import dataclass, field
from typing import List, Optional
from .gstin import validate_gstin

@dataclass
class Item:
    description: str
    hsn_code: str
    quantity: int
    price: float
    gst_rate: float  # e.g., 18 for 18%

    @property
    def taxable_value(self) -> float:
        return self.quantity * self.price

@dataclass
class Party:
    name: str
    gstin: str
    state_code: str

    def __post_init__(self):
        if not validate_gstin(self.gstin):
            raise ValueError("Invalid GSTIN")
        if self.state_code != self.gstin[:2]:
            raise ValueError("State code mismatch with GSTIN")

@dataclass
class Invoice:
    seller: Party
    buyer: Party
    items: List[Item]
    invoice_number: str
    place_of_supply: str
    cgst: float = 0.0
    sgst: float = 0.0
    igst: float = 0.0
    total: float = 0.0
    qr_data: Optional[str] = None

    def calculate_taxes(self):
        taxable_total = sum(i.taxable_value for i in self.items)
        self.total = taxable_total
        intrastate = self.seller.state_code == self.place_of_supply
        for item in self.items:
            tax = item.taxable_value * item.gst_rate / 100
            if intrastate:
                self.cgst += tax / 2
                self.sgst += tax / 2
            else:
                self.igst += tax
        self.total += self.cgst + self.sgst + self.igst
