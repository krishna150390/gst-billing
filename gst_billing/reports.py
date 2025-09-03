import csv
from typing import List
from fpdf import FPDF
from .invoice import Invoice


def _invoice_rows(invoices: List[Invoice]):
    """Convert invoices into rows for CSV/PDF output."""
    rows = []
    for inv in invoices:
        taxable = sum(i.taxable_value for i in inv.items)
        rows.append({
            "InvoiceNo": inv.invoice_number,
            "SellerGSTIN": inv.seller.gstin,
            "BuyerGSTIN": inv.buyer.gstin,
            "State": inv.place_of_supply,
            "TaxableValue": f"{taxable:.2f}",
            "CGST": f"{inv.cgst:.2f}",
            "SGST": f"{inv.sgst:.2f}",
            "IGST": f"{inv.igst:.2f}",
            "Total": f"{inv.total:.2f}",
        })
    return rows


def _write_csv(report_name: str, rows: List[dict], path: str) -> None:
    if not rows:
        raise ValueError("No data provided for report")
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def _write_pdf(report_name: str, rows: List[dict], path: str) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"{report_name} Report", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", size=10)
    for row in rows:
        line = ", ".join(f"{k}: {v}" for k, v in row.items())
        pdf.multi_cell(0, 5, line)
        pdf.ln(1)
    pdf.output(path)


def generate_gstr1(invoices: List[Invoice], csv_path: str, pdf_path: str) -> None:
    rows = _invoice_rows(invoices)
    _write_csv("GSTR-1", rows, csv_path)
    _write_pdf("GSTR-1", rows, pdf_path)


def generate_gstr2(invoices: List[Invoice], csv_path: str, pdf_path: str) -> None:
    rows = _invoice_rows(invoices)
    _write_csv("GSTR-2", rows, csv_path)
    _write_pdf("GSTR-2", rows, pdf_path)


def generate_gstr3b(invoices: List[Invoice], csv_path: str, pdf_path: str) -> None:
    rows = _invoice_rows(invoices)
    _write_csv("GSTR-3B", rows, csv_path)
    _write_pdf("GSTR-3B", rows, pdf_path)


def generate_gstr9(invoices: List[Invoice], csv_path: str, pdf_path: str) -> None:
    rows = _invoice_rows(invoices)
    _write_csv("GSTR-9", rows, csv_path)
    _write_pdf("GSTR-9", rows, pdf_path)
