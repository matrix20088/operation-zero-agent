#!/usr/bin/env python3
"""Read-only proof gate: verify actual Base USDC transfer to the owner's public address.

Only an actual successful USDC Transfer log from public Base RPC counts as cash.
No financial transactions are signed, sent, or paid. On failed/unknown reads
report pending, not paid. Never conflates SwarmMemo credits and USDC.
"""
import json
import urllib.request
from pathlib import Path
from decimal import Decimal
import re

ROOT=Path(__file__).resolve().parents[1]/"research"/"swarmmemo"
CLAIM=ROOT/"submission.json"
STATUS=ROOT/"payout_status.json"
TASK="09c1f608bbe17d729f034c1dae5b0a04"
USDC="0x833589fcd6edb6e08f4c7c32d4f71b54bda02913"
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
RPC="https://mainnet.base.org"

def json_get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"OperationZeroPublicProof/1.0","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)

def rpc(method,params):
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode()
    req=urllib.request.Request(RPC,data=body,headers={"Content-Type":"application/json"},method="POST")
    with urllib.request.urlopen(req,timeout=25) as r: return json.load(r).get("result")

def proof(txhash,recipient,amount):
    if not re.fullmatch(r"0x[0-9a-fA-F]{64}",txhash):return False,"invalid_tx_hash"
    tx=rpc("eth_getTransactionReceipt",[txhash])
    if not isinstance(tx,dict):return False,"receipt_missing"
    if tx.get("status")!="0x1":return False,"transaction_not_successful"
    target="0x"+recipient[2:].lower().rjust(64,"0")
    tokens=int(Decimal(amount)*Decimal(1_000_000))
    for log in tx.get("logs",[]):
        topics=log.get("topics") or []
        if (log.get("address","").lower()==USDC and len(topics)>=3
                and topics[0].lower()==TRANSFER and topics[2].lower()==target):
            value=int(log.get("data","0x0"),16)
            if value>=tokens:
                return True,"Base USDC Transfer confirmed in successful transaction receipt"
    return False,"No matching USDC transfer to the owner's address for the claimed amount"

def main():
    if not CLAIM.exists():
        print("No claim receipt exists. No payout to check.")
        return
    item=json.loads(CLAIM.read_text())
    if item.get("status") not in ("submitted","accepted","paid"):
        raise RuntimeError("Unrecognized submission status; no payout implied")
    address=item["payout_address"]
    report={"payout_received":False,"amount_usdc":"0","network":"Base","claim_id":item["reply_id"],"status":"awaiting_verdict_or_transfer"}
    task=json_get("https://swarmmemo.com/api/work/"+TASK)
    data=task.get("data",{}).get("work",{})
    matches=[r for r in data.get("results",[]) if r.get("result_id")==item["reply_id"] or r.get("work_id")==item["reply_id"]]
    if not matches:
        # Some standing rounds only expose a window of recent results.
        try:
            result=json_get("https://swarmmemo.com/api/work/"+item["reply_id"])
            matches=[result.get("data",{}).get("work",{})]
        except Exception: pass
    if matches:
        work=matches[0]
        money=work.get("money") or {}
        usdc=money.get("usdc") or work.get("reward_usdc") or {}
        state=usdc.get("state")
        txhash=usdc.get("tx_hash")
        pay_to=usdc.get("pay_to")
        amount=usdc.get("amount")
        report["platform_state"]=state
        if pay_to and pay_to.lower()!=address.lower():
            report["status"]="PAYMENT_ADDRESS_MISMATCH"
        elif state=="paid" and txhash and pay_to and amount:
            report["tx_hash"]=txhash
            report["tx_url"]="https://basescan.org/tx/"+txhash
            try:
                verified,note=proof(txhash,address,amount)
            except Exception as e:
                verified,note=False,"RPC confirmation unavailable: "+type(e).__name__
            report["chain_verification"]=note
            if verified:
                report.update({"payout_received":True,"amount_usdc":amount,"status":"CONFIRMED_USDC_ON_BASE"})
    if STATUS.exists() and json.loads(STATUS.read_text())==report:
        print("Payment state unchanged:",report["status"])
        return
    STATUS.write_text(json.dumps(report,indent=2)+"\n")
    print("Payment confirmed:",report["payout_received"],"USDC:",report["amount_usdc"],"status:",report["status"])

if __name__=="__main__":main()
