"""Third-path semantic oracle. Operates directly on abstract expressions and flat records.
Does not import lexicon.py or typed_control.py. This is still a *specified* oracle,
not independently discovered meaning or authenticated worldly truth.
"""

def truth(expression,ledger,t,k,c='default'):
    def eligible(x):
        return x['observed'] <= k and x['from'] <= t < x['until'] and c in x['contexts']
    def relation(rid):
        matches=[x for x in ledger['links'] if x['id']==rid and eligible(x)]
        if not matches:return 'U',None
        match=matches[0]
        accepted=[v for v in ledger['admissions'] if v['relation_id']==rid and v['observed']<=k]
        if not accepted:return 'U',match
        return ('T' if accepted[0]['outcome']=='ADMITTED' else 'F'),match
    def make(value,**kwargs):
        result={'value':value}
        for name in ['active','displaced','disputed','qualifiers','admitted','pending','support']:
            result[name]=sorted(set(kwargs.get(name,[])))
        return result
    kind=expression['op']
    if kind=='SCOPE':return truth(expression['body'],ledger,expression['query'],expression['knowledge'],expression['context'])
    if kind=='LINK':
        flag,r=relation(expression['id'])
        return make(flag,admitted=[expression['id']] if flag=='T' else [],
                    pending=[expression['id']] if flag=='U' and r else [],
                    support=r['evidence_ids'] if r and flag=='T' else [])
    if kind=='ATOM':
        statement=(expression['kind'],expression['predicate'],expression['subject'],expression['object'])
        pool={x['id']:x for x in ledger['claims'] if
              (x['kind'],x['predicate'],x['subject'],x['object'])==statement and eligible(x)}
        dismissed=[];challenged=[];tags=[];permitted=[];unconfirmed=[]
        citations=[x['source_id'] for x in pool.values()]
        for r in ledger['links']:
            if r['target'] not in pool or not eligible(r):continue
            source=next((x for x in ledger['claims'] if x['id']==r['source']),None)
            if source is None or not eligible(source):continue
            state,_=relation(r['id'])
            if state=='U':unconfirmed.append(r['id'])
            if state!='T':continue
            permitted.append(r['id']);citations+=r['evidence_ids']
            if r['kind']=='CORRECTS' or r['kind']=='SUPERSEDES':dismissed.append(r['target'])
            if r['kind']=='DISPUTES':challenged.append(r['target'])
            if r['kind']=='ADDS_CONTEXT':tags.append(r['source'])
        survivors=[x for x in pool.values() if x['id'] not in dismissed]
        vals={x['value'] for x in survivors}
        scalar=next(iter(vals)) if len(vals)==1 else 'U'
        return make(scalar,active=[x['id'] for x in survivors],displaced=dismissed,
                    disputed=challenged,qualifiers=tags,admitted=permitted,pending=unconfirmed,support=citations)
    if kind=='NOT':
        result=truth(expression['arg'],ledger,t,k,c)
        return {**result,'value':{'T':'F','F':'T','U':'U'}[result['value']]}
    if kind in ('ANY','ALL'):
        children=[truth(i,ledger,t,k,c) for i in expression['args']]
        values=[x['value'] for x in children]
        if kind=='ALL':value='F' if 'F' in values else 'U' if 'U' in values else 'T'
        else:value='T' if 'T' in values else 'U' if 'U' in values else 'F'
        return make(value,**{field:sum([x[field] for x in children],[])
                  for field in ['active','displaced','disputed','qualifiers','admitted','pending','support']})
    raise ValueError('not in frozen oracle grammar')
