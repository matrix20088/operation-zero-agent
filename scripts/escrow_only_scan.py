#!/usr/bin/env python3
"""Read-only escrow-backed task scout. No wallet, deposits or submissions."""
import datetime as dt
import json
import urllib.error
import urllib.parse
import urllib.request
import os
import re

BASE="https://api.taskmarket.dev"
CHAIN={"base":8453,"tempo":4217}
SKIP=re.compile(r"\b(tiktok|twitter|facebook|instagram|post a review|like and|follow and|refer friends|gambling|deploy to mainnet|sign a transaction|buy|purchase|stake|deposit|fund a task)\b",re.I)
GOOD=re.compile(r"\b(python|csv|markdown|json|script|api|fix|documentation|test|docs|automation|javascript|typescript|spreadsheet|analysis|parse|cli|bug|data|format|code|regex)\b",re.I)
def get(url):
 r=urllib.request.Request(url,headers={"User-Agent":"OperationZero-readonly-escrow-scout/1.0","Accept":"application/json"})
 with urllib.request.urlopen(r,timeout=25) as res:
  return json.loads(res.read(10000000))

def money(task):
 try:return int(task.get("netReward") or task["reward"])/1e6
 except (ValueError,TypeError,KeyError):return 0.

def do():
 now=dt.datetime.now(dt.timezone.utc)
 selected=[];stats=[];raw_samples=[]
 for chain,chainid in CHAIN.items():
  url=BASE+"/api/tasks?"+urllib.parse.urlencode(dict(chainId=chainid,status="open",mode="bounty",limit=100,sort="reward_desc"))
  try:response=get(url)
  except Exception as e:
   stats.append({"network":chain,"error":str(e)[:350]})
   continue
  tasks=response.get("tasks",[]) if isinstance(response,dict) else []
  stats.append({"network":chain,"scanned":len(tasks),"has_more":response.get("hasMore") if isinstance(response,dict) else None})
  if tasks:raw_samples.append({"network":chain,"keys":list(tasks[0].keys())})
  for t in tasks:
   if not isinstance(t,dict):continue
   reward=money(t)
   if not (1<=reward<=50):continue
   description=str(t.get("description") or "")
   if not GOOD.search(description) or SKIP.search(description):continue
   if not t.get("escrowTxHash"):continue
   if t.get("submissionWindowOpen") is not True:continue
   count=t.get("submissionCount",9999)
   if not isinstance(count,int) or count>12:continue
   task_id=t.get("id")
   if not task_id:continue
   exp=t.get("expiryTime")
   if exp:
    try:
     until=dt.datetime.fromisoformat(exp.replace("Z","+00:00"))
     if until<=now:continue
    except ValueError:continue
   detail={"id":task_id}
   try:detail=get(BASE+"/api/tasks/"+urllib.parse.quote(task_id)+"?chainId="+str(chainid))
   except Exception as e: detail["read_error"]=str(e)[:100]
   terms=detail.get("terms") or t.get("terms") or {}
   stake=terms.get("stake") or terms.get("stakeAmount") or t.get("stakeAmount") or t.get("claimDeposit") or 0
   if str(stake) not in ("0","0.0","None",""):continue
   record={"chain":chain,"amount_usd":reward,"id":task_id,"code":t.get("referenceCode"),"description":description[:2500],"submissions":count,"activity24h":t.get("recentActivityCount"),"expires":exp,"escrow":t.get("escrowTxHash"),"requester":t.get("requester"),"link":"https://taskmarket.dev/tasks/"+task_id,"terms":terms,"evaluation":detail.get("evaluator"),"payoutGate":detail.get("payoutGate"),"requiresTAP":detail.get("requiresTAP")}
   selected.append(record)
 selected.sort(key=lambda r:(r["submissions"],-r["amount_usd"]))
 result={"scanned_at":now.isoformat(),"stats":stats,"schema_samples":raw_samples,"candidates":selected[:70],"notice":"READ ONLY. Escrow is not guaranteed worker payout; requester/evaluator must approve. No funds spent or claims."}
 os.makedirs("research/escrow_scout",exist_ok=True)
 with open("research/escrow_scout/latest.json","w",encoding="utf8") as f:json.dump(result,f,ensure_ascii=False,indent=2)
 print("SCAN STATS",json.dumps(stats,ensure_ascii=False))
 print("SCHEMA",json.dumps(raw_samples,ensure_ascii=False))
 print("QUALIFIED LEADS",len(selected))
 for t in selected[:35]:
  print("\nTASK",json.dumps(t,ensure_ascii=False))
 if not selected:print("No escrow-backed low-competition tasks matching filters. No action.")
if __name__=="__main__":do()
