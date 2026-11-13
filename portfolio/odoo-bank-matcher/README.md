# Read-only bank matching preview for Odoo Accounting (portfolio sample)

A tiny, reproducible proof of concept for accountants who need an auditable **candidate** match list between a bank statement export and a general-ledger or payment export. It does **not** connect to Odoo, change accounts, perform reconciliation, or post journal entries.

This demonstration uses **fictional parties, amounts, and references**. No proprietary company data, payment credentials or real customer information are included.

## Example

```bash
python3 portfolio/odoo-bank-matcher/reconcile.py \
  --bank portfolio/odoo-bank-matcher/sample_bank.csv \
  --ledger portfolio/odoo-bank-matcher/sample_ledger.csv \
  --out reconciliation_candidates.csv
python3 -m unittest discover -s portfolio/odoo-bank-matcher -p 'test_*.py' -v
```

Expected candidate outcomes for the fixture:
- **B001:** one posted exact-amount, same-partner candidate in a 7-day date window
- **B002/B003:** possible duplicate transfer reference (both held for review)
- **B004:** unmatched because the corresponding ledger entry is draft, not posted

The CSV output has a stable `status` field, source bank identifiers and suggested journal identifier. Positive and negative amounts are **never** treated interchangeably, and all financial arithmetic uses Python `Decimal`, not floating point.

## Input columns

Bank CSV: `bank_id,date,partner,amount,reference`.
Odoo/payment ledger CSV: `ledger_id,date,partner,amount,reference,status`.
Dates are ISO (`YYYY-MM-DD`); amounts are signed, same-currency decimal values.

## Accounting safeguards

This is a **review aid only**: a same-amount bank line and ledger line are not proof of valid settlement, particularly where one is a clearing-account line or there are part payments, advances, 10% retentions, currency conversions, or multiple invoices. Every proposed match must be inspected against account types, posting state, actual invoice and transfer documentation, project/analytic allocation, and bank clearing accounts.

No taxes, customer balances, ledger status or VAT returns are changed. Producing a matching report is not the same as approving the bank reconciliation. Extensions for split transfers, tolerance, and actual Odoo exports are *possible work scopes*, not claimed capabilities of this sample.

## Buy a scoped review

[Fixed-price services](../../SERVICES.md) — discuss sample inputs, acceptance tests, currency treatment and secure handling privately before exchanging any real company data.
