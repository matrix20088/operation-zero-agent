#!/usr/bin/env python3
"""Read-only scan of dealwork: distinguish buyer jobs from seller advertisements."""
import json,urllib.request,urllib.parse,urllib.error,re,datetime as dt,os
U="https://api.dealwork.ai"
PATHS=["/api/v1/jobs?status=bidding&per_page=100","/api/v1/jobs?status=posted&per_page=100"]
def get(path):
 req=urllib.request.Request(U+path,headers={"User-Agent":"OperationZero-readonly-job-scan","Accept":"application/json"})
 with urllib.request.urlopen(req,timeout=18) as r:
  return json.loads(r.read(3000000))
def scan():
 sources=[];jobs=[]
 try:
  spec=get('/openapi.json')
  matches=[(k,v) for k,v in spec.get('paths',{}).items() if '/jobs' in k and 'get' in v]
  print('SWAGGER_GET_JOBS',json.dumps([{'path':k,'params':v.get('get',{}).get('parameters',[])} for k,v in matches[:10]],ensure_ascii=False)[:7000])
 except Exception as e:
  print('SWAGGER_ERR',str(e)[:300])
 for path in PATHS:
  try: v=get(path)
  except urllib.error.HTTPError as e:sources.append({"url":path,"error":str(e)[:120],"body":e.read().decode(errors="replace")[:700]});continue
  except Exception as e:sources.append({"url":path,"error":str(e)[:120]});continue
  entries=v if isinstance(v,list) else v.get("data",v.get("jobs",[]))
  if isinstance(entries,dict):entries=entries.get("jobs",entries.get("items",[]))
  if not isinstance(entries,list):
   sources.append({"url":path,"shape":list(v.keys()) if isinstance(v,dict) else type(v).__name__});continue
  sources.append({"url":path,"records":len(entries),"example_keys":list(entries[0].keys()) if entries and isinstance(entries[0],dict) else []})
  for t in entries:
   if not isinstance(t,dict):continue
   title=str(t.get("title") or "");body=str(t.get("description") or "")
   amount=t.get("budget") or t.get("budget_usd") or t.get("price") or 0
   try:
    if isinstance(amount,dict):amount=amount.get("max",amount.get("amount",0))
    amount=float(str(amount).replace("$",""))
   except (ValueError,TypeError):amount=0
   likely_ad=bool(re.search(r"\b(i offer|i am|I deliver|my service|order here|what you get|agent for hire|hire me|my rates)\b",title+" "+body,re.I))
   task=bool(re.search(r"\b(need|please|looking for|build|fix|create|implement|extract|convert|make|write|data|test)\b",title+" "+body,re.I))
   if not (3<=amount<=150 and task and not likely_ad):continue
   jobs.append({"id":t.get("id"),"title":title[:100],"budget":amount,"description":body[:850],"status":t.get("status"),"escrow":t.get("escrow_status") or t.get("escrow") or t.get("funded"),"bids":t.get("bid_count") or t.get("bids_count"),"link":t.get("url") or "https://api.dealwork.ai/explore","original_endpoint":path})
 os.makedirs("research/dealwork_scout",exist_ok=True)
 with open("research/dealwork_scout/latest.json","w") as f:json.dump({"sources":sources,"potential_jobs":jobs[:40]},f,indent=2,ensure_ascii=False)
 print("SOURCE_CHECKS",json.dumps(sources,ensure_ascii=False))
 print("POTENTIAL_BUYER_JOBS",len(jobs))
 for job in jobs[:25]:print("JOB",json.dumps(job,ensure_ascii=False))
 if not jobs:print("No verified buyer job found through public API; no bidding or payment")
if __name__=="__main__":scan()
