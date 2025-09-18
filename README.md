# gst-billing

This repository contains a minimal Python module demonstrating GST invoice
calculations for India. It is **not** a full featured billing application but a
starting point for experimenting with GST logic.

## Features

- GSTIN format validation with basic state code checks.
- Data classes for `Item`, `Party`, `Invoice`, `RecurringInvoiceTemplate` and
  `AdjustmentNote` with automatic CGST/SGST/IGST/UTGST calculations.
- Support for intra-state, inter-state, and union territory tax scenarios with
  e-invoice payload helpers.
- Optional QR code/IRN seed helper via deterministic hashing.
- Ledger utilities to post invoices, apply debit/credit notes, and reconcile
  purchase registers with GSTR-2A/2B data.
- Create basic GSTR-1, GSTR-2, GSTR-3B and GSTR-9 reports in CSV and PDF
  formats from invoices.
- Mockable GSTN client for uploading returns and generating IRN acknowledgments
  ready to be swapped with a real integration.

## Testing

Run unit tests with:

```bash
python -m unittest
```
