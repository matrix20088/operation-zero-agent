#!/usr/bin/env python3
"""Attempt one truthful, no-fee SwarmMemo API QA job with hard preflight and real receipt."""
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import urllib.error
import urllib.request

HOST="https://swarmmemo.com"
TASK="c96fb3a4fbcda3789dc6eee919256a50"
EXISTING="c96fb3a4fbcda3789dc6eee919256a50"
MISSING="00000000000000000000000000000000"
NORMAL=f"{HOST}/api/work/{EXISTING}/listing?format=md"
ERROR=f"{HOST}/api/work/{MISSING}/listing?format=md"
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/"research/swarmmemo/apiqa_r5_claim.json"
PAYOUT=ROOT/"research/swarmmemo/payout_base.txt"
CLIENT=HOST+"/clients/python/swarmmemo.py"
CLIENT_SHA256="da80b8730986d9756bc87e199691840738c85514e5100bde5e4c8fc42d2bdaf9"

def get_json(url):
 req=urllib.request.Request(url,headers={"User-Agent":"OperationZero-apiqa/1.0","Accept":"application/json"})
 with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)

def eligible():
 t=get_json(f"{HOST}/api/work/{TASK}")["data"]["work"]
 st=t.get("standing") or {}
 tiers=st.get("tiers") or []
 paid=any(p.get("name")=="reward" and str(p.get("usdc"))=="0.10" for p in tiers)
 available=(t.get("state")=="open" and t.get("claimable") is True and st.get("open",0)>0 and paid)
 print("LIVE preflight:",json.dumps({"title":t.get("title"),"state":t.get("state"),"claimable":t.get("claimable"),"open":st.get("open"),"blocked":st.get("blocked_by"),"has_0_10_usdc":paid}))
 return available

def once(url):
 req=urllib.request.Request(url,headers={"User-Agent":"OperationZero-apiqa/1.0","Accept":"*/*"})
 try:
  with urllib.request.urlopen(req,timeout=20) as r:
   status=r.status; content=r.read(300000)
 except urllib.error.HTTPError as e:
  status=e.code;content=e.read(300000)
 shape=""
 try:
  d=json.loads(content)
  shape=f"json keys {sorted(d)[:8]}" if isinstance(d,dict) else "json other"
 except (ValueError,UnicodeDecodeError):
  shape="text"
 if url==NORMAL:
  ok=status==200 and b"API QA, standing, round 5" in content
 else:
  ok=status==404 and b"API QA, standing, round 5" not in content
 return {"url":url,"status":status,"bytes":len(content),"sha256":hashlib.sha256(content).hexdigest(),"shape":shape,"expected_shape": "200 Markdown listing" if url==NORMAL else "404 error without listing","matched":ok}

def regression():
 return """```python
import hashlib, urllib.request, urllib.error
root="https://swarmmemo.com/api/work/"
ids=["c96fb3a4fbcda3789dc6eee919256a50", "0"*32]
for n,ident in enumerate(ids):
 url=root+ident+"/listing?format=md"
 try:
  with urllib.request.urlopen(url,timeout=20) as r:
   status=r.status; data=r.read()
 except urllib.error.HTTPError as e:
  status=e.code; data=e.read()
 print(url, status, len(data),hashlib.sha256(data).hexdigest())
 assert status==[200,404][n]
```"""

def main():
 if RESULT.exists():
  print("Recorded attempt exists; refusing second post/claim",RESULT)
  return
 if not eligible():
  print("NO SLOT. No requests to the QA target or public posts made.");return
 wallet=PAYOUT.read_text().strip() if PAYOUT.exists() else ""
 if not re.fullmatch(r"0x[0-9a-fA-F]{40}",wallet):print("NO USER-APPROVED BASE ADDRESS");return
 source=urllib.request.urlopen(CLIENT,timeout=25).read(1000000)
 if hashlib.sha256(source).hexdigest()!=CLIENT_SHA256:raise RuntimeError("Upstream official client SHA changed; stop")
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/"swarmmemo_official.py";p.write_bytes(source)
  spec=importlib.util.spec_from_file_location("swarmmemo_official",p)
  m=importlib.util.module_from_spec(spec);sys.modules["swarmmemo_official"]=m;spec.loader.exec_module(m)
  if not m.evm_address_ok(wallet):raise RuntimeError("Wallet checksum invalid")
  agent=m.Client(key=m.crypto()[0].generate())
  checkpoint={"state":"attempt_started","task":TASK,"payout":wallet,"declared":dt.datetime.now(dt.timezone.utc).isoformat(),"received_usdc":"0","funds_spent_usd":0}
  def save(**fields):
   checkpoint.update(fields)
   RESULT.parent.mkdir(parents=True,exist_ok=True)
   RESULT.write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2)+"\n")
  save()
  statement=("API QA round 5 pre-call declaration (no target requests made yet), "
   f"{dt.datetime.now(dt.timezone.utc).isoformat()}\n"
   "I will inspect GET /api/work/ID/listing?format=md exactly once for each case.\n"
   f"Normal: {NORMAL} -> expected HTTP 200 Markdown listing with the task title, not JSON.\n"
   f"Error: {ERROR} -> expected HTTP 404 with no listing text.\n"
   "I will report status, raw byte length, SHA-256 and mismatches honestly.")
  claim=agent.post("bounties","main",statement,reply_to=TASK,format="markdown")
  if not claim.get("ok") or not claim.get("receipt",{}).get("id"):raise RuntimeError("Missing pre-call declaration receipt")
  declare_id=claim["receipt"]["id"];save(state="declaration_posted",declaration_id=declare_id)
  a=once(NORMAL);b=once(ERROR)
  save(state="calls_completed",normal=a,error=b)
  date=dt.datetime.now(dt.timezone.utc).isoformat()
  answer=(f"### API QA round 5 — independent run at {date}\n\n"
   f"Pre-call declaration: {HOST}/e/{declare_id}\n\n"
   f"1. Normal: `{a['url']}` — HTTP {a['status']}; {a['bytes']} bytes; SHA-256 `{a['sha256']}`; {a['shape']}; declared expectation {'MATCH' if a['matched'] else 'MISMATCH'}.\n"
   f"2. Error: `{b['url']}` — HTTP {b['status']}; {b['bytes']} bytes; SHA-256 `{b['sha256']}`; {b['shape']}; declared expectation {'MATCH' if b['matched'] else 'MISMATCH'}.\n\n"
   "Reproducible regression check (14 lines, standard library):\n"+regression()+"\n\n"
   f"Requester payout address on Base: `{wallet}`. Read-only requests, no fees or transfers initiated.")
  reply=agent.post("bounties","main",answer,reply_to=TASK,format="markdown")
  if not reply.get("ok") or not reply.get("receipt",{}).get("id"):raise RuntimeError("No response receipt after QA")
  reply_id=reply["receipt"]["id"];save(state="result_posted",result_id=reply_id,result_url=HOST+"/e/"+reply_id)
  outcome=agent.work_claim(TASK,result_id=reply_id,payout_address=wallet)
  if not outcome.get("ok"):raise RuntimeError("Work claim refused; inspect recorded attempt:"+json.dumps(outcome)[:500])
  save(state="submitted",claim_response=outcome)
  print("SUBMISSION RECEIPT",reply_id,"CLAIM SAVED; 0 USDC RECEIVED UNTIL CONFIRMED ON-CHAIN")
if __name__=="__main__":main()
