#!/usr/bin/env python3
"""Read-only candidate matcher for Odoo exports and bank statements.

Never posts to Odoo. Amounts stay Decimal; only unique exact-amount partner matches
within a configurable date gap are candidates. Drafts, split payments,
duplicates and ambiguities require a human accountant.
"""
import argparse
import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import re
import unicodedata

def normalize(value):
    value = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", value)).strip()

def records(path, id_field):
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.DictReader(fh))
    required = {"date", "partner", "amount", id_field}
    if rows and not required.issubset(rows[0]):
        raise ValueError("Required columns: "+", ".join(sorted(required)))
    output = []
    for line, row in enumerate(rows, 2):
        try:
            amount=Decimal(str(row["amount"]).strip())
            if not amount.is_finite():raise ValueError("nonfinite amount")
            posted=date.fromisoformat(row["date"].strip())
            if not str(row[id_field]).strip():raise ValueError("blank identifier")
        except (InvalidOperation,ValueError,KeyError,TypeError) as e:
            raise ValueError(f"{path}: line {line}: invalid date/amount/id: {e}") from e
        record=dict(row)
        record.update({"_amount":amount,"_date":posted,"_partner":normalize(row["partner"])})
        output.append(record)
    return output

def reconcile(bank, ledger, max_days=7):
    dup_index=defaultdict(list)
    for item in bank:
        key=(normalize(item.get("reference","")), item["_amount"], item["_partner"])
        # Only nonempty original payment reference makes a duplicate flag reliable.
        if key[0]:dup_index[key].append(item["bank_id"])
    duplicate_ids={item_id for ids in dup_index.values() if len(ids)>1 for item_id in ids}
    used=set();results=[]
    for row in bank:
        base={"bank_id":row["bank_id"],"date":row["date"],"partner":row["partner"],"amount":str(row["_amount"])}
        if row["bank_id"] in duplicate_ids:
            results.append(dict(base,status="possible_duplicate_bank",ledger_id="",note="Repeated normalized reference/amount/partner; investigate originals"));continue
        candidates=[x for x in ledger
            if x["_amount"]==row["_amount"] and x["_partner"]==row["_partner"]
            and abs((x["_date"]-row["_date"]).days)<=max_days
            and x.get("status","posted").casefold()=="posted"
            and x["ledger_id"] not in used]
        if len(candidates)==1:
            x=candidates[0];used.add(x["ledger_id"])
            results.append(dict(base,status="candidate_unique",ledger_id=x["ledger_id"],
                note="Suggested match only: check invoice, payment and clearing-account direction in Odoo"))
        elif len(candidates)>1:
            results.append(dict(base,status="ambiguous_multiple_candidates",ledger_id="",
                note=f"{len(candidates)} possible journal lines; manual selection required"))
        else:
            results.append(dict(base,status="unmatched_bank",ledger_id="",
                note="No safe 1:1 posted candidate; check partial payments, drafts, unreconciled items"))
    return results

def main():
    ap=argparse.ArgumentParser(description="Read-only bank vs Odoo ledger reconciliation candidates")
    ap.add_argument("--bank",required=True)
    ap.add_argument("--ledger",required=True)
    ap.add_argument("--out",default="reconciliation_candidates.csv")
    ap.add_argument("--days",type=int,default=7)
    args=ap.parse_args()
    if not 0<=args.days<=90:ap.error("--days must be between 0 and 90")
    bank=records(args.bank,"bank_id")
    ledger=records(args.ledger,"ledger_id")
    rows=reconcile(bank,ledger,args.days)
    with open(args.out,"w",newline="",encoding="utf-8") as fh:
        writer=csv.DictWriter(fh,fieldnames=["bank_id","date","partner","amount","status","ledger_id","note"])
        writer.writeheader();writer.writerows(rows)
    counts={state:sum(r["status"]==state for r in rows) for state in sorted({r["status"] for r in rows})}
    print(json.dumps({"source_bank_rows":len(bank),"source_ledger_rows":len(ledger),"counts":counts,"output":args.out,
        "warning":"This is a candidate audit, not an Odoo posting or proof of bank reconciliation."},indent=2))
if __name__=="__main__":main()
