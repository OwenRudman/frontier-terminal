import json, re
d=json.load(open('frontier_data.json'))
# strip holdings (public build)
for vk in d['verticals']:
    for t,c in d['verticals'][vk]['companies'].items(): c['hold']=None
# collect real sell-side firm names from the data, add common short variants
firms=set()
for vk in d['verticals']:
    for t,c in d['verticals'][vk]['companies'].items():
        for n in (c.get('streetNotes') or []):
            if isinstance(n,dict) and n.get('firm'): firms.add(str(n['firm']).strip())
firms |= {'Goldman','Wainwright','HC Wainwright','Raymond James','Jefferies','Needham','BTIG','GSBR','Jones'}
# longest first so multi-word names match before short forms
patterns=sorted({f for f in firms if len(f)>=3}, key=len, reverse=True)
def scrub_text(s):
    for f in patterns:
        s=re.sub(r'\b'+re.escape(f)+r'\b','sell-side',s)
    s=s.replace('sell-side, sell-side','sell-side').replace('sell-side and sell-side','sell-side')
    return s
def walk(o):
    if isinstance(o,dict): return {k:walk(v) for k,v in o.items()}
    if isinstance(o,list): return [walk(v) for v in o]
    if isinstance(o,str): return scrub_text(o)
    return o
d=walk(d)
# generic provenance label + anonymize per-note firm + tidy street.source
prov=(d.get('provenance') or {}).get('street')
if isinstance(prov,dict): prov['src']='Sell-side consensus + internal estimates'
for vk in d['verticals']:
    for t,c in d['verticals'][vk]['companies'].items():
        st=c.get('street')
        if isinstance(st,dict) and st.get('source'):
            st['source']=re.sub(r'\s*:.*$','',str(st['source'])).strip()
        sn=c.get('streetNotes')
        if isinstance(sn,list):
            for i,n in enumerate(sn):
                if isinstance(n,dict) and n.get('firm'):
                    n['firm']='Firm '+chr(65+i) if i<26 else 'Firm'
json.dump(d,open('frontier_data.json','w'),indent=1)
shell=open('shell.html').read(); engine=open('engine.js').read()
open('index.html','w').write(shell.replace('/*DATA*/',json.dumps(d)).replace('/*ENGINE*/',engine))
print('built index.html (holdings stripped, sell-side names scrubbed)')
