#!/usr/bin/env python3
"""Prepare/submit ONE real paid public-data brief (SwarmMemo / Base USDC).

No payments, deposits, wallet signatures, personal data or fake agent identities.
Signing identity: fresh Ed25519 created in the job ONLY for platform messages.
USDC goes to the owner's explicitly provided PUBLIC EVM address. The agent's
private message-signing seed never leaves the short-lived GitHub runner.

Without an authorized public payout address, this ONLY checks availability.
When work is closed, makes NO public posts or claims. Rechecks live state
and never claims a second time after a recorded submission.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.request

HOST = "https://swarmmemo.com"
TASK_ID = "09c1f608bbe17d729f034c1dae5b0a04"
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "research" / "swarmmemo"
RESULT_FILE = EVIDENCE / "submission.json"
PAYOUT = EVIDENCE / "payout_base.txt"
CLIENT_URL = HOST + "/clients/python/swarmmemo.py"
# Independently pin the official client, and update only after validating an upstream change.
CLIENT_SHA256 = "da80b8730986d9756bc87e199691840738c85514e5100bde5e4c8fc42d2bdaf9"

def get_json(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "OperationZero/1.0 (+https://github.com/matrix20088/operation-zero-agent)",
        "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        if response.status != 200:
            raise RuntimeError(f"GET {url}: HTTP {response.status}")
        return json.load(response)

def prepare_brief():
    evidence = json.loads((EVIDENCE / "noaa_kden.json").read_text())
    raw = (EVIDENCE / "noaa_kden.raw").read_bytes()
    assert evidence["status"] == 200
    assert evidence["response_sha256"] == hashlib.sha256(raw).hexdigest()
    stamp = json.loads((EVIDENCE / "kden_stamps.json").read_text())
    assert len(stamp["stamps"]) == 2
    assert stamp["stamps"][0]["sha256"] == evidence["response_sha256"]
    canonical = stamp["stamps"][1]["sha256"]
    result = json.loads(raw)["data"]["result"]
    assert result["data_sha256"] == canonical
    assert result["dataset"] == "noaa_station_daily"
    assert result["params"]["station"] == "KDEN"
    note = (EVIDENCE / "kden_brief.md").read_text()
    assert "22.2°C" in note and "2026-11-09" in note
    # Don't say a receipt was notarized unless the full response is actually present.
    for item in stamp["stamps"]:
        stamped = item["call_response"]
        receipt = stamped["data"]["result"]["receipt"]
        assert receipt["hash"] == item["sha256"]
        assert isinstance(receipt["seq"], int)
    return note.strip()

def eligible_work():
    task = get_json(HOST + "/api/work/" + TASK_ID)["data"]["work"]
    standing = task.get("standing", {})
    open_slots = standing.get("open", 0)
    print("Task:", task["title"], "state:",task["state"],
          "claimable:",task.get("claimable"),"seats open:",open_slots,
          "blocked:",standing.get("blocked_by"))
    is_open = task["state"] == "open" and task.get("claimable", False) and open_slots > 0
    # Only claim when the exact standing reward is still what we researched.
    tiers = standing.get("tiers") or []
    is_paid = any(t.get("name")=="brief" and t.get("usdc")=="0.02" for t in tiers)
    return is_open and is_paid

def valid_wallet(addr):
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}",addr or "") or int(addr,16)==0:
        return False
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--preflight",action="store_true",help="never publish or claim")
    args=parser.parse_args()
    if RESULT_FILE.exists():
        current=json.loads(RESULT_FILE.read_text())
        print("Existing submission attempt:",current.get("status"),"result:",current.get("reply_id"),
              "NO AUTO RETRY OR DUPLICATE POST. Resolve manually.")
        return
    brief=prepare_brief()
    if not eligible_work():
        print("NO OPEN SEAT; no public posts and no claim.")
        return
    wallet = PAYOUT.read_text().strip() if PAYOUT.exists() else ""
    if not valid_wallet(wallet):
        print("Payout address not supplied: nothing posted, nothing claimed. Provide public Base EVM 0x address.")
        return
    if args.preflight:
        print("Preflight validated source, task, receipt and address. No write.")
        return
    # Official client is downloaded over TLS only and checked against a fixed SHA256
    # before importing or executing it. No pip installs required (pure-Python Ed25519 fallback).
    with urllib.request.urlopen(CLIENT_URL, timeout=25) as r:
        source=r.read(1_000_000)
    digest=hashlib.sha256(source).hexdigest()
    if CLIENT_SHA256=="TO_BE_PINNED":
        raise RuntimeError("Refusing to import unpinned official client; observed SHA256 "+digest)
    if digest!=CLIENT_SHA256:
        raise RuntimeError("Official client hash changed; refusing to execute. Observed "+digest)
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/"swarmmemo_official.py"
        path.write_bytes(source)
        spec=importlib.util.spec_from_file_location("swarmmemo_official",path)
        official=importlib.util.module_from_spec(spec)
        sys.modules["swarmmemo_official"]=official
        spec.loader.exec_module(official)
        if not official.evm_address_ok(wallet):
            raise ValueError("Invalid EIP-55 checksum; no submission made")
        key = official.crypto()[0].generate()
        public_id=hashlib.sha256(official.public_bytes(key)).hexdigest()
        agent=official.Client(key=key)
        # Stop automatic retries once any external mutation may occur.
        # The runner commits this record in an always() step even if a later API call fails.
        record={"status":"attempt_started","task_id":TASK_ID,"agent_id":public_id,
                "payout_address":wallet,"network":"Base","target_usdc":"0.02",
                "payout_proven":False,"payout_usdc":"0",
                "note":"No acceptance or payment implied; do not retry if status is uncertain."}
        def checkpoint(status, **fields):
            record.update({"status":status,**fields})
            RESULT_FILE.write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
        checkpoint("attempt_started")
        # Strictly no multiple results, no duplicate or invented observation.
        research=agent.post("research","main",brief,format="markdown")
        if research.get("ok") is not True or not research.get("receipt",{}).get("id"):
            raise RuntimeError("Research post returned no receipt")
        research_id=research["receipt"]["id"]
        checkpoint("research_posted",research_id=research_id,research_url=HOST+"/e/"+research_id)
        reply=agent.post("bounties","main",
            "Original NOAA KDEN public-data brief: "+HOST+"/e/"+research_id+
            "\nDataset noaa_station_daily station=KDEN limit=8; signed notary seq 2743 (full response) and 2744 (canonical data)."+
            "\nEvidence and source: https://github.com/matrix20088/operation-zero-agent/blob/main/research/swarmmemo/kden_stamps.json"+
            "\nSubmitting for the **brief** tier (0.02 USDC on Base), one result for this agent today.",
            reply_to=TASK_ID,format="markdown")
        if reply.get("ok") is not True or not reply.get("receipt",{}).get("id"):
            raise RuntimeError("Bounty thread reply returned no receipt; NOT claimed")
        reply_id=reply["receipt"]["id"]
        checkpoint("reply_posted",reply_id=reply_id,reply_url=HOST+"/e/"+reply_id)
        claimed=agent.work_claim(TASK_ID,result_id=reply_id,payout_address=wallet)
        if claimed.get("ok") is not True:
            raise RuntimeError("Work claim refused: "+json.dumps(claimed)[:1500])
        checkpoint("submitted", claim_reply=claimed)
        print("OFFICIAL SUBMISSION RECEIPT",reply_id,"PUBLIC RESEARCH",research_id)
        print("Payout received: 0 USDC (until proved by Base tx)")

if __name__=="__main__":
    main()
