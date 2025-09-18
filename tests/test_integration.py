import unittest

from gst_billing.integration import GSTNClient, GSTNIntegrationError
from gst_billing.invoice import Invoice, Item, Party


class GSTNClientTest(unittest.TestCase):
    def setUp(self):
        self.client = GSTNClient(base_url="https://api.gst.gov.in")
        self.client.authenticate("client", "secret")
        seller = Party(name="Seller", gstin="27ABCDE1234F1Z5", state_code="27")
        buyer = Party(name="Buyer", gstin="29ABCDE1234F1Z5", state_code="29")
        item = Item(description="Service", hsn_code="9985", quantity=1, price=100.0, gst_rate=18)
        self.invoice = Invoice(
            seller=seller,
            buyer=buyer,
            items=[item],
            invoice_number="INV100",
            place_of_supply="29",
        )

    def test_upload_return(self):
        ack = self.client.upload_return("GSTR1", {"test": "value"})
        self.assertTrue(ack.startswith("ACK-GSTR1"))

    def test_generate_irn_requires_payload(self):
        payload = self.invoice.to_einvoice_payload()
        irn = self.client.generate_irn(payload)
        self.assertEqual(irn, payload["Irn"])

    def test_fetch_gstr2b_requires_gstin(self):
        data = self.client.fetch_gstr2b("27ABCDE1234F1Z5")
        self.assertEqual(data["gstin"], "27ABCDE1234F1Z5")

    def test_upload_return_without_auth(self):
        client = GSTNClient(base_url="https://api.gst.gov.in")
        with self.assertRaises(GSTNIntegrationError):
            client.upload_return("GSTR1", {})


if __name__ == "__main__":
    unittest.main()
