#!/usr/bin/env python3
"""Public read-only view of escrowed, unassigned claim jobs with zero worker stake."""
import datetime as dt,json,os,urllib.parse,urllib.request
def fetch(url):
 req=urllib.request.Request(url,headers={'Accept':'application/json','User-Agent':'OperationZero-claim-preflight/1.0'})
 with urllib.request.urlopen(req,timeout=25) as r:return json.load(r)
def main():
 rows=[];counts=[];now=dt.datetime.now(dt.timezone.utc)
 for network,chain in [('Base',8453),('Tempo',4217)]:
  for mode in ('claim','pitch','bounty'):
   url='https://api.taskmarket.dev/api/tasks?'+urllib.parse.urlencode({'chainId':chain,'status':'open','mode':mode,'limit':100,'sort':'newest'})
   try:
    data=fetch(url)
   except Exception as ex:
    counts.append({'network':network,'mode':mode,'error':str(ex)[:200]});continue
   tasks=data.get('tasks',[])
   counts.append({'network':network,'mode':mode,'n':len(tasks),'more':data.get('hasMore')})
   for item in tasks:
    try:reward=int(item.get('netReward') or item['reward'])/1e6
    except (ValueError,KeyError,TypeError):continue
    if reward<1 or reward>50:continue
    if not item.get('escrowTxHash'):continue
    if item.get('stakeRequired') or int(item.get('stakeBps') or 0)>0:continue
    if item.get('submissionWindowOpen') is False and mode=='bounty':continue
    expiry=item.get('expiryTime') or ''
    try:
     if dt.datetime.fromisoformat(expiry.replace('Z','+00:00'))<=now:continue
    except ValueError:continue
    row={'network':network,'mode':mode,'reward':reward,'code':item.get('referenceCode'),'id':item.get('id'),'desc':item.get('description','')[:4000],'submissions':item.get('submissionCount'),'recent':item.get('recentActivityCount'),'escrow_tx':item.get('escrowTxHash'),'expires':expiry,'terms':item.get('terms'),'url':'https://taskmarket.dev/tasks/'+item.get('id','')}
    rows.append(row)
 rows.sort(key=lambda x:({'claim':0,'pitch':1,'bounty':2}[x['mode']], -x['reward'], x['submissions'] or 0))
 os.makedirs('research/claimable_scout',exist_ok=True)
 with open('research/claimable_scout/nov13.json','w') as f:json.dump({'counts':counts,'tasks':rows},f,ensure_ascii=False,indent=2)
 print('COUNTS:',json.dumps(counts))
 print('ELIGIBLE_ZERO_STAKE_ESCROW',len(rows))
 for row in rows[:40]:print('TASK:',json.dumps(row,ensure_ascii=False))
if __name__=='__main__':main()
