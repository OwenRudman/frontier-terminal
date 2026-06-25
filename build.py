import json, os
shell=open('shell.html').read()
data=open('frontier_data.json').read()
engine=open('engine.js').read()
if os.environ.get('STRIP_HOLDINGS'):
    d=json.loads(data)
    for vk in d['verticals']:
        for t,c in d['verticals'][vk]['companies'].items(): c['hold']=None
    data=json.dumps(d)
open('index.html','w').write(shell.replace('/*DATA*/',data).replace('/*ENGINE*/',engine))
print('built index.html')
