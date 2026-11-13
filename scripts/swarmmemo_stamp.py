#!/usr/bin/env python3
"""Notarize the exact already-fetched NOAA response with a free SwarmMemo notary.

Evidence kept in GitHub, no paid requests and no task claim. Idempotent hash stamps.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

OUT=Path("research/swarmmemo")
RAW=OUT/"noaa_kden.raw"
SOURCE=OUT/"noaa_kden.json"
evidence=json.loads(SOURCE.read_text())
raw=RAW.read_bytes()
rawsha=hashlib.sha256(raw).hexdigest()
assert evidence["status"]==200 and evidence["response_sha256"]==rawsha
body=json.loads(raw)
assert body.get("ok") is True
result=body["data"]["result"]
assert result["dataset"]=="noaa_station_daily"
assert result["params"]["station"]=="KDEN"
data=result["data"]
canonical=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()
assert canonical==result["data_sha256"],(canonical,result["data_sha256"])
assert data["requested_station"]=="KDEN"
byday={day["date"]:day for day in data["days"]}
assert "2026-11-09" in byday and "2026-11-02" in byday
new,old=byday["2026-11-09"],byday["2026-11-02"]

stamps=[]
for label,value in [("full_response",rawsha),("dataset_data",canonical)]:
    url="https://swarmmemo.com/call/notary/stamp?"+urlencode({"hash":value})
    req=Request(url,headers={"User-Agent":"OperationZero/1.0","Accept":"application/json"})
    with urlopen(req,timeout=25) as r:
        stamped=json.loads(r.read(150_000))
        status=r.status
    print("notary stamp",label,status,JSON_VALUE if False else value)
    if status!=200 or stamped.get("ok") is not True:
        raise RuntimeError(f"Notary {label} failed: {stamped}")
    stamps.append({"label":label,"sha256":value,"call_response":stamped})
record={"source":evidence,"notary_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"stamps":stamps}
(OUT/"kden_stamps.json").write_text(json.dumps(record,indent=2,ensure_ascii=False)+"\n")
rtext=[]
for s in stamps:
    res=s["call_response"]
    dataobj=res.get("data") or {}
    receipt=dataobj.get("result") or dataobj.get("receipt") or dataobj
    rtext.append(f"{s['label']}: SHA256 {s['sha256']}; notary response "+json.dumps(receipt,ensure_ascii=False)[:1200])
brief=(
f"**NOAA KDEN (Denver airport, USW00003017), latest published {result['as_of']}** — high {new['tmax_c']}°C, low {new['tmin_c']}°C, peak gust {new['peak_gust_mph']} mph and {new['precip_mm']} mm precipitation on {new['date']}.\n"
f"**Change:** on {old['date']} high {old['tmax_c']}°C and gust {old['peak_gust_mph']} mph; by {new['date']} high rose {round(new['tmax_c']-old['tmax_c'],1)}°C while peak gust fell {round(old['peak_gust_mph']-new['peak_gust_mph'],1)} mph (daily summaries, not a weather forecast).\n"
f"**Data gap:** requested through {result['params']['end_date']}, but newest available observation is {result['as_of']}; tool displays {len(data['days'])} recent rows from {data['count']} days, so days after Nov 9 are NOT claimed to be observed.\n"
f"**Source and exact arguments:** NOAA NCEI GHCN-Daily; dataset=noaa_station_daily, station=KDEN, limit=8, source {result['source_url']}; retrieved {result['fetched_at']}.\n"
f"**Reproduce:** full HTTP response SHA-256 {rawsha}; canonical data SHA-256 {canonical}; notarized hashes and receipts in https://github.com/matrix20088/operation-zero-agent/blob/main/research/swarmmemo/kden_stamps.json."
)
(OUT/"kden_brief.md").write_text(brief+"\n")
print(brief)
