import os
import csv
import tempfile
import unittest

from gst_billing import (
    Item,
    Party,
    Invoice,
    generate_gstr1,
    generate_gstr2,
    generate_gstr3b,
    generate_gstr9,
)


class ReportGenerationTest(unittest.TestCase):
    def setUp(self):
        self.seller = Party(name="Seller", gstin="27ABCDE1234F1Z5", state_code="27")
        self.buyer = Party(name="Buyer", gstin="29ABCDE1234F1Z5", state_code="29")
        self.items = [Item(description="Service", hsn_code="9985", quantity=1, price=1000.0, gst_rate=18)]

    def _invoice(self):
        invoice = Invoice(
            seller=self.seller,
            buyer=self.buyer,
            items=self.items,
            invoice_number="INV001",
            place_of_supply="29",
        )
        invoice.calculate_taxes()
        return invoice

    def _check_files(self, csv_path, pdf_path):
        self.assertTrue(os.path.exists(csv_path))
        self.assertTrue(os.path.exists(pdf_path))
        with open(csv_path) as fh:
            reader = csv.DictReader(fh)
            rows = list(reader)
            self.assertEqual(rows[0]["InvoiceNo"], "INV001")
        self.assertGreater(os.path.getsize(pdf_path), 0)

    def test_gstr1_generation(self):
        invoice = self._invoice()
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = os.path.join(tmp, "gstr1.csv")
            pdf_path = os.path.join(tmp, "gstr1.pdf")
            generate_gstr1([invoice], csv_path, pdf_path)
            self._check_files(csv_path, pdf_path)

    def test_other_reports_generation(self):
        invoice = self._invoice()
        with tempfile.TemporaryDirectory() as tmp:
            gstr2_csv = os.path.join(tmp, "gstr2.csv")
            gstr2_pdf = os.path.join(tmp, "gstr2.pdf")
            gstr3b_csv = os.path.join(tmp, "gstr3b.csv")
            gstr3b_pdf = os.path.join(tmp, "gstr3b.pdf")
            gstr9_csv = os.path.join(tmp, "gstr9.csv")
            gstr9_pdf = os.path.join(tmp, "gstr9.pdf")
            generate_gstr2([invoice], gstr2_csv, gstr2_pdf)
            generate_gstr3b([invoice], gstr3b_csv, gstr3b_pdf)
            generate_gstr9([invoice], gstr9_csv, gstr9_pdf)
            for csv_file, pdf_file in [
                (gstr2_csv, gstr2_pdf),
                (gstr3b_csv, gstr3b_pdf),
                (gstr9_csv, gstr9_pdf),
            ]:
                self._check_files(csv_file, pdf_file)


if __name__ == "__main__":
    unittest.main()
