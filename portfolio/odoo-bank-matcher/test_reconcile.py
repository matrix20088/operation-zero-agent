import sys
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from reconcile import normalize,reconcile

def row(ident, partner, amount, day="2026-11-11", reference="", status="posted", bank=True):
    return {"bank_id" if bank else "ledger_id":ident, "date":day,"partner":partner,"amount":amount,
            "status":status,"reference":reference,"_amount":Decimal(amount),
            "_date":date.fromisoformat(day),"_partner":normalize(partner)}

class MatcherTests(unittest.TestCase):
    def test_exact_unique_candidate(self):
        out=reconcile([row("b1","Acme LLC","-1250.25")],[row("l1","ACME LLC","-1250.25", bank=False)])
        self.assertEqual(out[0]["status"],"candidate_unique")
        self.assertEqual(out[0]["ledger_id"],"l1")
    def test_never_auto_match_draft(self):
        out=reconcile([row("b1","Supplier","-500")],[row("l1","Supplier","-500",status="draft",bank=False)])
        self.assertEqual(out[0]["status"],"unmatched_bank")
    def test_ambiguous_remains_unmatched(self):
        out=reconcile([row("b1","Vendor","-50")],[row("a","Vendor","-50",bank=False),row("b","Vendor","-50",bank=False)])
        self.assertEqual(out[0]["status"],"ambiguous_multiple_candidates")
    def test_duplicate_bank_reference(self):
        bank=[row("b1","Vendor","-50",reference="TR-100"),row("b2","Vendor","-50",reference="TR-100")]
        out=reconcile(bank,[row("l1","Vendor","-50",bank=False)])
        self.assertTrue(all(x["status"]=="possible_duplicate_bank" for x in out))
    def test_sign_and_date_preserved(self):
        out=reconcile([row("b1","Vendor","-50")],[row("l1","Vendor","50",bank=False)])
        self.assertEqual(out[0]["status"],"unmatched_bank")
        out=reconcile([row("b1","Vendor","-50")],[row("l1","Vendor","-50","2026-10-20",bank=False)])
        self.assertEqual(out[0]["status"],"unmatched_bank")
if __name__=="__main__":unittest.main()
