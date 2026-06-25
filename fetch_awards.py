import json, time, requests
d=json.load(open('frontier_data.json'))
URL='https://api.usaspending.gov/api/v2/search/spending_by_award/'
def awards(name):
    body={"filters":{"recipient_search_text":[name],"award_type_codes":["A","B","C","D"],
        "time_period":[{"start_date":"2024-01-01","end_date":"2026-12-31"}]},
        "fields":["Award ID","Recipient Name","Award Amount","Awarding Agency","Description","Start Date"],
        "limit":4,"sort":"Award Amount","order":"desc"}
    try:
        r=requests.post(URL,json=body,timeout=35); out=[]
        for x in r.json().get('results',[]):
            amt=x.get('Award Amount') or 0
            if amt and amt>0:
                out.append({"amt":amt,"ag":x.get('Awarding Agency'),"desc":x.get('Description'),"date":x.get('Start Date')})
        return out
    except Exception: return []
cnt=0; seen={}
for vk in d['verticals']:
    for t,c in d['verticals'][vk]['companies'].items():
        if not c.get('pub'): continue
        if t in seen: c['awards']=seen[t]; continue
        a=awards(c.get('n',t)); seen[t]=a
        if a: c['awards']=a; cnt+=1
        time.sleep(0.4)
json.dump(d,open('frontier_data.json','w'),indent=1)
print('awards set on',cnt,'companies')
