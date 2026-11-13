#!/usr/bin/env python3
"""Read-only public microgig radar: candidates are never proof of cash."""
import datetime as dt
import html
from html.parser import HTMLParser
import json
import os
import re
import urllib.request
import urllib.error

SOURCES = {
 "jobbi": "https://jobbi.org/gigs.json?lane=agent&limit=700",
 "swarmmemo": "https://swarmmemo.com/api/works?kind=rewarded&limit=100",
 "taskmarket": "https://taskmarket.dev/tasks?chain=8453",
}
BAD = re.compile(r"\b(kyc|deposit required|stake required|pay a fee|must deposit|registration fee|seed phrase|first fund a bounty)\b", re.I)
TECH = re.compile(r"\b(python|typescript|javascript|github|bug|csv|json|markdown|api|docs|test|script|data|validation|automation|documentation|fix|qa|programming)\b", re.I)

class Text(HTMLParser):
 def __init__(self): super().__init__(); self.data = []
 def handle_data(self, part): self.data.append(part)

def fetch(url):
 req = urllib.request.Request(url, headers={"User-Agent":"MatrixTaskAgent-readonly/1.0", "Accept":"application/json,text/html"})
 with urllib.request.urlopen(req, timeout=25) as resp:
  return resp.read(3000000).decode("utf8", "replace")

def rows(payload):
 if isinstance(payload, list): return payload
 if not isinstance(payload,dict): return []
 for key in ("items","gigs","works","data","results","tasks"):
  value=payload.get(key)
  if isinstance(value,list): return value
  if isinstance(value,dict):
   for nested in ("items","gigs","works","results"):
    if isinstance(value.get(nested),list): return value[nested]
 return []

def cash(item):
 for key in ("reward_usd","reward_amount_usd","amount_usd","payout_usd","bounty_usd"):
  value=item.get(key)
  if value is not None:
   try: return float(str(value).replace("$","").replace(",",""))
   except (ValueError,TypeError): pass
 reward=item.get("reward")
 if isinstance(reward,dict):
  currency=str(reward.get("currency") or "").upper()
  if currency in ("USD","USDC","USDT"):
   try: return float(reward.get("amount",reward.get("value")))
   except (ValueError,TypeError): return None
 if isinstance(reward,str):
  match=re.search(r"(?:\$|USD\s*|USDC\s*)([\d,.]+)",reward,re.I)
  if match: return float(match.group(1).replace(",",""))
 return None

def jobbi(payload):
 out=[]
 entries=rows(payload)
 for item in entries:
  if not isinstance(item,dict): continue
  name=str(item.get("title") or item.get("name") or "")
  details=str(item.get("content_text") or item.get("summary") or item.get("description") or "")
  if str(item.get("lane","")).lower()=="human" or BAD.search(name+" "+details) or not TECH.search(name+" "+details): continue
  value=cash(item)
  if value is None:
   for key in ("_jobbi","_gig","metadata"):
    if isinstance(item.get(key),dict): value=cash(item[key]);break
  if value is None or not (0.01<=value<=20): continue
  url=str(item.get("url") or item.get("external_url") or "")
  # BountyBook's public board has no escrowed listings and repeated payout failures.
  # AgentBounties' legacy "funded" issues have no currently claimable-live issues.
  if any(domain in url.lower() for domain in ("api.bountybook.ai/", "api.agentbounties.app/", "oss.issuehunt.io/")): continue
  out.append({"source":"jobbi/"+str(item.get("source") or item.get("board") or "?"),"title":name[:130],"usd":value,"url":url,"verification":"unverified: inspect original posting and escrow"})
 return out,len(entries)

def swarmmemo(payload):
 out=[]
 entries=rows(payload)
 for item in entries:
  if not isinstance(item,dict): continue
  reward=item.get("reward") or {}
  reward=reward if isinstance(reward,dict) else {}
  tiers=reward.get("tiers") or (item.get("data") or {}).get("tiers") or []
  values=[]
  for part in [reward]+[x for x in tiers if isinstance(x,dict)]:
   try: values.append(float(part.get("usdc") or part.get("usdc_amount") or 0))
   except (ValueError,TypeError): pass
  value=max(values or [0])
  standing=item.get("standing") or {}
  seats=standing.get("open") if isinstance(standing,dict) else None
  if not (0.01<=value<=20) or seats is not None and seats<=0 or str(item.get("state") or item.get("status") or "") in ("closed","expired","cancelled"): continue
  title=str(item.get("title") or (item.get("data") or {}).get("title") or "")
  if BAD.search(title):continue
  out.append({"source":"swarmmemo","title":title[:130],"usd":value,"url":"https://swarmmemo.com/work/"+str(item.get("id") or item.get("work_id") or ""),"seats":seats,"verification":"unverified: sponsor-funded USDC is not escrowed; credits are not cash"})
 return out,len(entries)

def taskmarket(raw):
 p=Text(); p.feed(raw)
 plain=html.unescape(" ".join(p.data))
 out=[]
 for m in re.finditer(r"Open for submissions.{0,400}",plain,re.I):
  desc=" ".join(m.group(0).split())
  reward=re.search(r"\$([0-9,.]+)",desc)
  if not reward or not TECH.search(desc) or BAD.search(desc): continue
  try:amount=float(reward.group(1).replace(",",""))
  except ValueError:continue
  if not (0.5<=amount<=20):continue
  out.append({"source":"taskmarket/base","title":desc[:150],"usd":amount,"url":SOURCES["taskmarket"],"verification":"unverified: reward may be split across winners; individual escrow and rules must be checked"})
 return out[:30],len(plain)

def main():
 candidates=[];checks=[];utc=dt.datetime.now(dt.timezone.utc).isoformat()
 for name,url in SOURCES.items():
  try:
   raw=fetch(url)
   if name=="jobbi":
    payload=json.loads(raw);selected,n=jobbi(payload)
   elif name=="swarmmemo":
    payload=json.loads(raw);selected,n=swarmmemo(payload)
   else:selected,n=taskmarket(raw)
   candidates.extend(selected)
   checks.append({"source":name,"scanned":n,"selected":len(selected),"schema":list(payload.keys())[:10] if name!="taskmarket" and isinstance(payload,dict) else []})
  except (OSError,ValueError,urllib.error.URLError,TypeError) as e:
   checks.append({"source":name,"error":type(e).__name__+":"+str(e)[:150]})
 candidates.sort(key=lambda item:(item["usd"]>5, item["usd"],item["source"]))
 result={"checked_at_utc":utc,"checks":checks,"candidates":candidates[:80],"real_cash_received_usd":0,"note":"Read-only; no claims, accounts, payments or delivered work. All listings are leads, not certified funded and open."}
 os.makedirs("research/hidden_radar",exist_ok=True)
 with open("research/hidden_radar/latest.json","w",encoding="utf8") as file:json.dump(result,file,ensure_ascii=False,indent=2)
 lines=["# Hidden-paid-work radar","",utc,"","**Read only — no money earned and no jobs claimed.**","", "## Source checks"]
 for c in checks:lines.append("- "+json.dumps(c,ensure_ascii=False))
 lines+=["","## Candidate microgigs — manual escrow / availability verification required"]
 for item in candidates[:30]:
  lines.append("- $%.2f [%s] %s — %s"%(item["usd"],item["source"],item["title"].replace("\n"," ")[:90],item["url"]))
 lines+=["","Never submit unless there is a real funded reward, available slot, clear test, and real payout evidence.",""]
 report="\n".join(lines)
 with open("research/hidden_radar/latest.md","w",encoding="utf8") as file:file.write(report)
 print(report)
 summary=os.environ.get("GITHUB_STEP_SUMMARY")
 if summary:
  with open(summary,"a",encoding="utf8") as file:file.write(report)

if __name__=="__main__": main()
