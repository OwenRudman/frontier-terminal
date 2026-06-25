import json, datetime
import yfinance as yf
d=json.load(open('frontier_data.json'))
tks=set()
for vk in d['verticals']:
    for t,c in d['verticals'][vk]['companies'].items():
        if c.get('pub') and t.isalpha() and len(t)<=5: tks.add(t)
ok=0
for t in sorted(tks):
    try:
        fi=yf.Ticker(t).fast_info
        last=fi.get('last_price'); prev=fi.get('previous_close')
        if last:
            chg=round((last/prev-1)*100,2) if prev else 0
            for vk in d['verticals']:
                if t in d['verticals'][vk]['companies']:
                    d['verticals'][vk]['companies'][t]['px']=round(float(last),2)
                    d['verticals'][vk]['companies'][t]['chg']=chg
            ok+=1
    except Exception: pass
d['prices_asof']=datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
json.dump(d,open('frontier_data.json','w'),indent=1)
print('prices set on',ok,'tickers')
