import json, datetime
import yfinance as yf
d=json.load(open('frontier_data.json'))
tks=set()
for vk in d['verticals']:
    for t,c in d['verticals'][vk]['companies'].items():
        if c.get('pub') and t.isalpha() and len(t)<=5: tks.add(t)

def parse_news(raw):
    out=[]
    for it in (raw or [])[:4]:
        c=it.get('content') if isinstance(it.get('content'),dict) else it
        title=c.get('title') or it.get('title')
        if not title: continue
        pub=it.get('publisher')
        prov=c.get('provider')
        if isinstance(prov,dict): pub=prov.get('displayName') or pub
        link=it.get('link')
        for k in ('clickThroughUrl','canonicalUrl'):
            v=c.get(k)
            if isinstance(v,dict) and v.get('url'): link=v['url']; break
        ts=it.get('providerPublishTime'); date=''; sortts=0
        if isinstance(ts,(int,float)):
            date=datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d'); sortts=ts
        else:
            pd=c.get('pubDate') or it.get('pubDate') or ''
            date=(pd or '')[:10]
            try: sortts=datetime.datetime.fromisoformat(pd.replace('Z','+00:00')).timestamp()
            except: sortts=0
        out.append({'h':title,'pub':pub or '','link':link or '','date':date,'_ts':sortts})
    return out

ok=0; glob=[]
for t in sorted(tks):
    tk=None
    try:
        tk=yf.Ticker(t); fi=tk.fast_info
        last=fi.get('last_price'); prev=fi.get('previous_close')
        if last:
            chg=round((last/prev-1)*100,2) if prev else 0
            for vk in d['verticals']:
                if t in d['verticals'][vk]['companies']:
                    d['verticals'][vk]['companies'][t]['px']=round(float(last),2)
                    d['verticals'][vk]['companies'][t]['chg']=chg
            ok+=1
    except Exception: pass
    try:
        if tk is None: tk=yf.Ticker(t)
        nn=parse_news(tk.news)
        if nn:
            for vk in d['verticals']:
                if t in d['verticals'][vk]['companies']:
                    d['verticals'][vk]['companies'][t]['news']=[{k:v for k,v in n.items() if k!='_ts'} for n in nn[:3]]
            for n in nn: glob.append({'tk':t, **n})
    except Exception: pass

glob.sort(key=lambda x:x.get('_ts',0), reverse=True)
d['news']=[{'tk':n['tk'],'h':n['h'],'pub':n['pub'],'link':n['link'],'date':n['date']} for n in glob[:40]]
d['prices_asof']=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
json.dump(d,open('frontier_data.json','w'),indent=1)
print('prices set on',ok,'tickers; news items',len(d['news']))
