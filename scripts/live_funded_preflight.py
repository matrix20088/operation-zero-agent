#!/usr/bin/env python3
"""One-shot preflight for fundable remote tasks. Reads public providers ONLY."""
import json,urllib.request,urllib.error,datetime as dt,re,pathlib
H={"User-Agent":"OperationZero/2.0 (+https://github.com/matrix20088/operation-zero-agent)","Accept":"application/json"}
URLS={
 "execution_available":"https://api.execution.market/api/v1/tasks/available?limit=100",
 "execution_tasks":"https://api.execution.market/api/v1/tasks?status=published&limit=100",
 "moltjobs":"https://api.moltjobs.io/v1/jobs?status=OPEN&limit=100",
 "makefun_requirements":"https://make.fun/api/competitions/news-image-01/requirements",
 "swarmmemo_data":"https://swarmmemo.com/api/work/09c1f608bbe17d729f034c1dae5b0a04",
}
def get(url):
 req=urllib.request.Request(url,headers=H)
 try:
  with urllib.request.urlopen(req,timeout=22) as res:
   return {"http":res.status,"payload":json.load(res)}
 except urllib.error.HTTPError as e:
  return {"http":e.code,"error":e.read(600).decode(errors="replace")}
 except Exception as e:return {"error":type(e).__name__+": "+str(e)[:200]}
def extract(payload):
 if isinstance(payload,list):return payload
 if not isinstance(payload,dict):return []
 for k in ("tasks","jobs","items","results","data"):
  value=payload.get(k)
  if isinstance(value,list):return value
  if isinstance(value,dict):
   for kk in ("tasks","jobs","items","results"):
    if isinstance(value.get(kk),list):return value[kk]
 return []
def main():
 out={"checked_utc":dt.datetime.now(dt.timezone.utc).isoformat(),"sources":{}}
 for name,url in URLS.items():
  result=get(url);data=result.get("payload")
  if name=="makefun_requirements":
   d=data.get("data",data) if isinstance(data,dict) else data
   out["sources"][name]={"http":result.get("http"),"prerequisites":d.get("prerequisites") if isinstance(d,dict) else None,
      "handed_over_places":d.get("handed_over_places") if isinstance(d,dict) else None,"bundle_required":d.get("deliverables") if isinstance(d,dict) else None,
      "raw":str(d)[:5000] if isinstance(d,dict) else result.get("error")}
  elif name=="swarmmemo_data":
   d=data.get("data",{}).get("work",{}) if isinstance(data,dict) else {}
   out["sources"][name]={"http":result.get("http"),"title":d.get("title"),"state":d.get("state"),"claimable":d.get("claimable"),"standing":d.get("standing"),
     "results":str(d.get("results"))[:250]}
  else:
   records=extract(data)
   results=[]
   for item in records:
    if not isinstance(item,dict):continue
    words=str(item.get("title",""))+" "+str(item.get("description",""))
    if re.search(r"Python|coding|data|research|analysis|software|csv|audit|API|documentation|web|report|automation|typescript|script",words,re.I):
     results.append({k:item.get(k) for k in ("id","title","status","budget","reward","price","payout","escrowStatus","escrow_tx","escrowTxHash","funded","assigned_to","deadline","category","type","created_at") if k in item})
     results[-1]["brief"]=str(item.get("description",""))[:1300]
   out["sources"][name]={"http":result.get("http"),"error":result.get("error"),
       "total_records":len(records),"sample_keys":list(records[0].keys()) if records and isinstance(records[0],dict) else [],
       "filtered":results[:25],"other_shape":list(data)[:14] if isinstance(data,dict) else None}
 pathlib.Path("research/funded_preflight").mkdir(parents=True,exist_ok=True)
 pathlib.Path("research/funded_preflight/latest.json").write_text(json.dumps(out,indent=2,ensure_ascii=False))
 print(json.dumps(out,indent=2,ensure_ascii=False)[:55000])
 print("NO SUBMISSIONS OR PAID ACTIONS MADE")
if __name__=="__main__":main()
