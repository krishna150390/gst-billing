import unittest
from gst_billing.invoice import Item, Party, Invoice

class InvoiceTest(unittest.TestCase):
    def setUp(self):
        self.seller = Party(name="Seller", gstin="27ABCDE1234F1Z5", state_code="27")
        self.buyer = Party(name="Buyer", gstin="29ABCDE1234F1Z5", state_code="29")
        self.items = [Item(description="Service", hsn_code="9985", quantity=1, price=1000.0, gst_rate=18)]

    def test_interstate_tax(self):
        invoice = Invoice(seller=self.seller, buyer=self.buyer, items=self.items,
                          invoice_number="INV001", place_of_supply="29")
        invoice.calculate_taxes()
        self.assertEqual(invoice.igst, 180.0)
        self.assertEqual(invoice.cgst, 0.0)
        self.assertEqual(invoice.sgst, 0.0)
        self.assertEqual(invoice.total, 1180.0)

    def test_intrastate_tax(self):
        invoice = Invoice(seller=self.seller, buyer=self.seller, items=self.items,
                          invoice_number="INV002", place_of_supply="27")
        invoice.calculate_taxes()
        self.assertEqual(invoice.cgst, 90.0)
        self.assertEqual(invoice.sgst, 90.0)
        self.assertEqual(invoice.igst, 0.0)
        self.assertEqual(invoice.total, 1180.0)

if __name__ == "__main__":
    unittest.main()
