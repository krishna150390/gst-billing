import unittest
from datetime import date

from gst_billing.accounting import (
    Ledger,
    apply_adjustment_note,
    entries_for_invoice,
    reconcile_with_gstr2a,
)
from gst_billing.invoice import AdjustmentNote, Invoice, Item, Party


class AccountingTest(unittest.TestCase):
    def setUp(self):
        self.seller = Party(name="Seller", gstin="27ABCDE1234F1Z5", state_code="27")
        self.buyer = Party(name="Buyer", gstin="29ABCDE1234F1Z5", state_code="29")
        self.item = Item(
            description="Goods",
            hsn_code="9985",
            quantity=1,
            price=500.0,
            gst_rate=18,
        )

    def create_invoice(self, invoice_number: str, place_of_supply: str) -> Invoice:
        return Invoice(
            seller=self.seller,
            buyer=self.buyer,
            items=[self.item],
            invoice_number=invoice_number,
            place_of_supply=place_of_supply,
            invoice_date=date(2023, 4, 1),
        )

    def test_entries_for_invoice(self):
        invoice = self.create_invoice("INV-001", "29")
        entries = entries_for_invoice(invoice)
        accounts = {entry.account for entry in entries}
        self.assertIn("Accounts Receivable", accounts)
        self.assertIn("Sales", accounts)
        self.assertIn("Output IGST", accounts)

    def test_apply_adjustment_note(self):
        ledger = Ledger(name="AR")
        invoice = self.create_invoice("INV-002", "29")
        note = AdjustmentNote(
            reference_invoice=invoice,
            note_number="CN-100",
            amount=50.0,
            reason="Price adjustment",
            is_credit=True,
        )
        apply_adjustment_note(ledger, note)
        self.assertEqual(len(ledger.entries), 1)
        self.assertEqual(ledger.entries[0].debit, 50.0)

    def test_reconcile_with_gstr2a(self):
        purchase_invoices = [
            self.create_invoice("PINV-1", "29"),
            self.create_invoice("PINV-2", "29"),
        ]
        gstr2a = [self.create_invoice("PINV-1", "29")]
        missing = reconcile_with_gstr2a(purchase_invoices, gstr2a)
        self.assertEqual(missing, ["PINV-2"])


if __name__ == "__main__":
    unittest.main()
