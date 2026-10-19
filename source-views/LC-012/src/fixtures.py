"""Controlled synthetic facts; no claim about physical observations or real authority."""
import copy
from contract import blank,POLICY

def ev(id,t):return dict(id=id,source_id='synthetic-'+id,description='Declared fixture '+id,observed=t)
def claim(id,value,t=0,kind='observation',pred='sealed',contexts=None):
    return dict(id=id,kind=kind,predicate=pred,subject='A',object='B',value=value,
                observed=t,**{'from':0,'until':20},contexts=contexts or ['default','lab'],source_id='e-'+id)
def condition(id,key,value,t=0):
    return dict(id=id,key=key,value=value,observed=t,**{'from':0,'until':20},
                contexts=['default','lab'],source_id='e-'+id)
def relation(id,kind,source,target,t=0,guard=None,contexts=None):
    return dict(id=id,kind=kind,source=source,target=target,observed=t,
                **{'from':0,'until':20},contexts=contexts or ['default','lab'],evidence_ids=['e-'+id],
                guard=guard if guard is not None else ['CONST','T'])
def reviewer(name='r-general',allowed=None,contexts=None):
    return dict(id=name,allowed_kinds=allowed or sorted(POLICY),
                contexts=contexts or ['default','lab'],**{'from':0,'until':20})
def admit(id,kind,when=0,who='r-general',outcome='ADMITTED'):
    return dict(id='review-'+id,relation_id=id,reviewer_id=who,rule=POLICY[kind],
                observed=when,evidence_ids=['e-'+id],outcome=outcome)

def addclaim(L,c):L['evidence'].append(ev(c['source_id'],c['observed']) if c['source_id']=='e-'+c['id'] else ev(c['source_id'],c['observed']));L['claims'].append(c)
def addcondition(L,condition):L['evidence'].append(ev(condition['source_id'],condition['observed']));L['conditions'].append(condition)
def addrelation(L,link,approval=True):
    L['evidence'].append(ev(link['evidence_ids'][0],link['observed']));L['links'].append(link)
    if approval:L['admissions'].append(admit(link['id'],link['kind'],link['observed']))

def episode():
    L=blank();L['reviewers'].append(reviewer());snapshots=[]
    addclaim(L,claim('original','T',0));snapshots.append(copy.deepcopy(L))
    addclaim(L,claim('later','F',1));snapshots.append(copy.deepcopy(L))
    addrelation(L,relation('fix-original','CORRECTS','later','original',2));snapshots.append(copy.deepcopy(L))
    addclaim(L,claim('restored','T',3));addrelation(L,relation('fix-later','CORRECTS','restored','later',3))
    snapshots.append(copy.deepcopy(L))
    addrelation(L,relation('cycle','CORRECTS','later','restored',4));snapshots.append(copy.deepcopy(L))
    return snapshots

ATOM={'op':'ATOM','kind':'observation','predicate':'sealed','subject':'A','object':'B'}
def to_lex(e):
    op=e['op']
    if op=='ATOM':return ['ATOM',e['kind'],e['predicate'],e['subject'],e['object']]
    if op=='LINK':return ['LINK',e['id']]
    if op=='NOT':return ['NOT',to_lex(e['arg'])]
    if op=='SCOPE':return ['SCOPE',e['query'],e['knowledge'],e['context'],to_lex(e['body'])]
    if op not in ('ALL','ANY'):raise ValueError('unrecognized abstract expression operation')
    return [('AND' if op=='ALL' else 'OR')]+[to_lex(x) for x in e['args']]
