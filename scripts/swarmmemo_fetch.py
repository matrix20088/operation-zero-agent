#!/usr/bin/env python3
"""Fetch original public-data tool responses for the 0.02 USDC SwarmMemo brief.

Read only. No jobs are claimed; no rewards assumed. All outputs attributed to source.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError,URLError
import datetime as dt, hashlib, json, urllib.parse

HOST="https://swarmmemo.com"
DATASETS={
    "noaa_kden":("noaa_station_daily", {"station":"KDEN","limit":"8"}),
    "fx_eur":("fx_rates", {}),
    "ai_arena":("ai_model_leaderboard", {}),
}
URLS={key: HOST+"/call/public_data/fetch?"+urllib.parse.urlencode({"dataset":dataset,**args}) for key,(dataset,args) in DATASETS.items()}
URLS["task_thread"]=HOST+"/api/thread/09c1f608bbe17d729f034c1dae5b0a04?limit=100"
out=Path("research/swarmmemo")
out.mkdir(parents=True,exist_ok=True)

for key,url in URLS.items():
    headers={"User-Agent":"OperationZero/1.0 (+github.com/matrix20088/operation-zero-agent)","Accept":"application/json"}
    request=Request(url,headers=headers)
    try:
        with urlopen(request,timeout=30) as res:
            body=res.read(2_000_001);status=res.status
    except HTTPError as e:
        body=e.read(2_000_001);status=e.code
    except (URLError, TimeoutError) as e:
        body=json.dumps({"network_error":str(e)}).encode();status=0
    rawsha=hashlib.sha256(body).hexdigest()
    try:
        parsed=json.loads(body)
        if isinstance(parsed,dict):
            data=parsed.get("data")
            if data and isinstance(data,dict):
                if "result" in data and "data" in data["result"]:
                    data=data["result"]["data"]
                elif "data" in data:
                    data=data["data"]
            canonical=hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest() if data is not None else None
        else: canonical=None
    except ValueError: parsed={"error":"not JSON"};canonical=None
    evidence={"fetched_at_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"url":url,"status":status,"response_sha256":rawsha,"canonical_data_sha256":canonical,"size":len(body),"response":parsed}
    (out/(key+".raw")).write_bytes(body)
    (out/(key+".json")).write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(key,status,len(body),rawsha,"canonical",canonical)
