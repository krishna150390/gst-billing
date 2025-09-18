import unittest
from datetime import date

from gst_billing.invoice import (
    AdjustmentNote,
    Item,
    Invoice,
    Party,
    RecurringInvoiceTemplate,
)


class InvoiceTest(unittest.TestCase):
    def setUp(self):
        self.seller = Party(name="Seller", gstin="27ABCDE1234F1Z5", state_code="27")
        self.buyer = Party(name="Buyer", gstin="29ABCDE1234F1Z5", state_code="29")
        self.items = [
            Item(
                description="Service",
                hsn_code="9985",
                quantity=1,
                price=1000.0,
                gst_rate=18,
            )
        ]

    def test_interstate_tax(self):
        invoice = Invoice(
            seller=self.seller,
            buyer=self.buyer,
            items=self.items,
            invoice_number="INV001",
            place_of_supply="29",
        )
        invoice.calculate_taxes()
        self.assertEqual(invoice.igst, 180.0)
        self.assertEqual(invoice.cgst, 0.0)
        self.assertEqual(invoice.sgst, 0.0)
        self.assertEqual(invoice.total, 1180.0)

    def test_intrastate_tax(self):
        invoice = Invoice(
            seller=self.seller,
            buyer=self.seller,
            items=self.items,
            invoice_number="INV002",
            place_of_supply="27",
        )
        invoice.calculate_taxes()
        self.assertEqual(invoice.cgst, 90.0)
        self.assertEqual(invoice.sgst, 90.0)
        self.assertEqual(invoice.igst, 0.0)
        self.assertEqual(invoice.total, 1180.0)

    def test_union_territory_tax(self):
        seller = Party(name="UT Seller", gstin="04ABCDE1234F1Z5", state_code="04")
        buyer = Party(name="UT Buyer", gstin="04ABCDE1234F1Z5", state_code="04")
        invoice = Invoice(
            seller=seller,
            buyer=buyer,
            items=self.items,
            invoice_number="INV003",
            place_of_supply="04",
        )
        invoice.calculate_taxes()
        self.assertEqual(invoice.cgst, 90.0)
        self.assertEqual(invoice.utgst, 90.0)
        self.assertEqual(invoice.sgst, 0.0)

    def test_einvoice_payload_contains_irn(self):
        invoice = Invoice(
            seller=self.seller,
            buyer=self.buyer,
            items=self.items,
            invoice_number="INV004",
            place_of_supply="29",
            invoice_date=date(2023, 4, 1),
        )
        payload = invoice.to_einvoice_payload()
        self.assertIn("Irn", payload)
        self.assertEqual(payload["DocDtls"]["Dt"], "01/04/2023")
        self.assertEqual(invoice.qr_data, payload["Irn"])

    def test_recurring_invoice_template(self):
        template = RecurringInvoiceTemplate(
            template_name="Monthly Service",
            seller=self.seller,
            buyer=self.buyer,
            items=self.items,
            billing_cycle_days=30,
            next_invoice_date=date(2023, 4, 1),
        )
        invoice = template.generate_invoice("INV005")
        self.assertEqual(invoice.total, 1180.0)
        template.advance_cycle()
        self.assertEqual(template.next_invoice_date, date(2023, 5, 1))

    def test_adjustment_note(self):
        invoice = Invoice(
            seller=self.seller,
            buyer=self.buyer,
            items=self.items,
            invoice_number="INV006",
            place_of_supply="29",
        )
        note = AdjustmentNote(
            reference_invoice=invoice,
            note_number="CN-1",
            amount=100.0,
            reason="Discount",
            is_credit=True,
        )
        self.assertEqual(note.ledger_impact()["debit"], 100.0)


if __name__ == "__main__":
    unittest.main()
