import json, datetime, requests
d=json.load(open('frontier_data.json'))
tks=set()
for vk in d['verticals']:
    for t,c in d['verticals'][vk]['companies'].items():
        if c.get('pub'): tks.add(t)
soc={}
for p in range(1,9):
    try:
        r=requests.get(f'https://apewisdom.io/api/v1.0/filter/all-stocks/page/{p}',timeout=25)
        for x in r.json().get('results',[]):
            if x.get('ticker') in tks:
                soc[x['ticker']]={'m':x.get('mentions',0),'m0':x.get('mentions_24h_ago') or 0,'rk':x.get('rank'),'up':x.get('upvotes',0)}
    except Exception: pass
d['social_asof']=datetime.date.today().isoformat()
for vk in d['verticals']:
    for t,c in d['verticals'][vk]['companies'].items():
        c['social']=soc.get(t)
json.dump(d,open('frontier_data.json','w'),indent=1)
print('buzz set on',len(soc))
