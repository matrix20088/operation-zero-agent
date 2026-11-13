#!/usr/bin/env python3
"""Probe WURK's documented public job discovery without account or payments."""
import urllib.request,urllib.error,re,json,datetime as dt,os
HOST='https://api.wurk.fun'
H={'User-Agent':'OperationZero-Worker-Preflight/1.0','Accept':'application/json'}
def fetch(path,accept='application/json'):
 h=dict(H);h['Accept']=accept
 req=urllib.request.Request(HOST+path,headers=h)
 try:
  with urllib.request.urlopen(req,timeout=25) as r:return {'status':r.status,'body':r.read(1_500_000).decode('utf-8','replace')}
 except urllib.error.HTTPError as e:return {'status':e.code,'body':e.read(800).decode('utf-8','replace')}
 except Exception as e:return {'error':type(e).__name__+': '+str(e)[:200]}
def main():
 x=fetch('/references/worker.md','text/markdown')
 doc=x.get('body','')
 lines=doc.splitlines()
 keylines=[]
 for i,line in enumerate(lines):
  if re.search(r'GET |public|list jobs|public job|explore|/jobs|/work',line,re.I):
   keylines.append({'line':i+1,'text':line[:240]})
 print('WORKER GUIDE status',x.get('status'),'length',len(doc),'relevant lines',json.dumps(keylines[:85],ensure_ascii=False))
 probes=[
  '/v1/jobs?status=active&limit=100',
  '/v1/jobs?limit=100',
  '/jobs?limit=100',
  '/api/jobs?limit=100',
  '/v1/work/jobs?status=active&limit=100',
  '/v1/work/jobs?limit=100',
  '/v1/custom-jobs?limit=100',
 ]
 outcomes=[]
 for p in probes:
  r=fetch(p)
  item={'endpoint':p,'status':r.get('status'),'error':r.get('error')}
  body=r.get('body','')
  if r.get('status')==200:
   try:
    z=json.loads(body)
    item['shape']=list(z)[:20] if isinstance(z,dict) else type(z).__name__
    result=z.get('data',z) if isinstance(z,dict) else z
    if isinstance(result,dict):
     for k in ('jobs','items','tasks','results'):
      if isinstance(result.get(k),list):
       item['n']=len(result[k]);item['examples']=[{'title':str(a.get('title',''))[:150],'reward':a.get('reward'),'status':a.get('status'),'allowsAgents':a.get('allowsAgents'),'id':a.get('id'),'endsAt':a.get('endsAt')} for a in result[k][:20] if isinstance(a,dict)];break
    if 'examples' not in item:item['sample']=body[:2000]
   except ValueError:item['sample']=body[:800]
  else:item['sample']=body[:350]
  outcomes.append(item)
 print('PROBES',json.dumps(outcomes,ensure_ascii=False,indent=2)[:18000])
 os.makedirs('research/wurk',exist_ok=True)
 with open('research/wurk/public_scan.json','w') as f:json.dump({'at':dt.datetime.now(dt.timezone.utc).isoformat(),'worker_doc_code':x.get('status'),'worker_guide_keys':keylines,'probes':outcomes,'notes':'read-only, no registration or funds spent'},f,indent=2,ensure_ascii=False)
if __name__=='__main__':main()
