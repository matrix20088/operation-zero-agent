#!/usr/bin/env python3
"""Read-only discovery for a real SwarmMemo public-data micro-bounty.

No credentials, claims, or posts. Data is public and third party.
Outputs machine-readable evidence rather than filling guessed figures.
"""
from __future__ import annotations
from pathlib import Path
import datetime as dt
import hashlib
import json
import urllib.error
import urllib.request

HOST="https://swarmmemo.com"
TARGETS={
 "datasets": HOST + "/call/public_data/datasets",
 "active_task": HOST + "/api/work/09c1f608bbe17d729f034c1dae5b0a04",
 "works": HOST + "/api/works?kind=rewarded&limit=30",
}
OUTPUT=Path("research/swarmmemo")
OUTPUT.mkdir(parents=True,exist_ok=True)

def fetch(name, url):
    request=urllib.request.Request(url,headers={"User-Agent":"operation-zero-agent/0.1 (+https://github.com/matrix20088/operation-zero-agent)","Accept":"application/json"})
    try:
        with urllib.request.urlopen(request,timeout=20) as response:
            payload=response.read(1_000_001)
            status=response.status
            content_type=response.headers.get("Content-Type","")
    except urllib.error.HTTPError as e:
        payload=e.read(1_000_001); status=e.code;content_type=e.headers.get("Content-Type","")
    digest=hashlib.sha256(payload).hexdigest()
    raw=OUTPUT/(name+".raw")
    raw.write_bytes(payload)
    try: data=json.loads(payload)
    except ValueError: data={"raw_text":payload[:1000].decode("utf-8","replace")}
    result={"utc":dt.datetime.now(dt.timezone.utc).isoformat(),"request":url,"status":status,"content_type":content_type,"bytes":len(payload),"sha256_raw":digest,"body":data}
    (OUTPUT/(name+".json")).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(f"{name}: HTTP {status}, {len(payload)} bytes, SHA256 {digest}")
    print("Top-level keys:",list(data)[:20] if isinstance(data,dict) else "not object")
    return result

def main():
    results={name:fetch(name,url) for name,url in TARGETS.items()}
    if any(r["status"] != 200 for r in results.values()):
        raise SystemExit("One or more reads were not HTTP 200; inspect evidence, no task claimed.")

if __name__=="__main__":main()
