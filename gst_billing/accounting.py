"""Utilities for ledger accounting and GST reconciliation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, List

from .invoice import AdjustmentNote, Invoice


@dataclass
class LedgerEntry:
    entry_date: date
    account: str
    debit: float = 0.0
    credit: float = 0.0
    reference: str = ""

    def __post_init__(self) -> None:
        if self.debit < 0 or self.credit < 0:
            raise ValueError("Debit and credit values cannot be negative")
        if self.debit and self.credit:
            raise ValueError("An entry cannot have both debit and credit values")


@dataclass
class Ledger:
    name: str
    entries: List[LedgerEntry] = field(default_factory=list)

    def add_entry(self, entry: LedgerEntry) -> None:
        self.entries.append(entry)

    def balance(self) -> float:
        debit = sum(e.debit for e in self.entries)
        credit = sum(e.credit for e in self.entries)
        return debit - credit


def entries_for_invoice(invoice: Invoice) -> List[LedgerEntry]:
    """Create accounting entries for a sales invoice."""

    invoice.calculate_taxes()
    entries = [
        LedgerEntry(
            entry_date=invoice.invoice_date,
            account="Accounts Receivable",
            debit=round(invoice.total, 2),
            reference=invoice.invoice_number,
        ),
        LedgerEntry(
            entry_date=invoice.invoice_date,
            account="Sales",
            credit=round(invoice.taxable_total, 2),
            reference=invoice.invoice_number,
        ),
    ]

    if invoice.cgst:
        entries.append(
            LedgerEntry(
                entry_date=invoice.invoice_date,
                account="Output CGST",
                credit=round(invoice.cgst, 2),
                reference=invoice.invoice_number,
            )
        )
    if invoice.sgst:
        entries.append(
            LedgerEntry(
                entry_date=invoice.invoice_date,
                account="Output SGST",
                credit=round(invoice.sgst, 2),
                reference=invoice.invoice_number,
            )
        )
    if invoice.utgst:
        entries.append(
            LedgerEntry(
                entry_date=invoice.invoice_date,
                account="Output UTGST",
                credit=round(invoice.utgst, 2),
                reference=invoice.invoice_number,
            )
        )
    if invoice.igst:
        entries.append(
            LedgerEntry(
                entry_date=invoice.invoice_date,
                account="Output IGST",
                credit=round(invoice.igst, 2),
                reference=invoice.invoice_number,
            )
        )

    return entries


def apply_adjustment_note(ledger: Ledger, note: AdjustmentNote) -> None:
    impacts = note.ledger_impact()
    ledger.add_entry(
        LedgerEntry(
            entry_date=date.today(),
            account="Accounts Receivable",
            debit=impacts["debit"],
            credit=impacts["credit"],
            reference=note.note_number,
        )
    )


def reconcile_with_gstr2a(purchase_register: Iterable[Invoice], gstr2a_invoices: Iterable[Invoice]) -> List[str]:
    """Return a list of invoice numbers that require reconciliation."""

    expected = {inv.invoice_number: inv for inv in purchase_register}
    matched = {inv.invoice_number for inv in gstr2a_invoices}
    missing = [inv_no for inv_no in expected.keys() if inv_no not in matched]
    return sorted(missing)
