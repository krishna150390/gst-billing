# gst-billing

This repository contains a minimal Python module demonstrating GST invoice
calculations for India. It is **not** a full featured billing application but a
starting point for experimenting with GST logic.

## Features

- GSTIN format validation with basic state code checks.
- Data classes for `Item`, `Party`, and `Invoice` with automatic tax
  calculations.
- Supports intra-state (CGST + SGST) and inter-state (IGST) scenarios based on
  place of supply.
- Optional QR code generation helper.

## Testing

Run unit tests with:

```bash
python -m unittest
```
