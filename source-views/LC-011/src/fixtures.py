"""Canonical declared synthetic scenario, not physical-event evidence."""
import copy
from contracts import make_ledger

def ev(id,at):return {'id':id,'source_id':id+'-fictional-source','description':'synthetic '+id,'observed':at}
def claim(id,kind,pred,sub,obj,val,at,src,contexts=None):
    return dict(id=id,kind=kind,predicate=pred,subject=sub,object=obj,value=val,
                observed=at,**{'from':0,'until':12},contexts=contexts or ['default','lab'],source_id=src)
def link(id,kind,src,target,at,evidence,contexts=None):
    return dict(id=id,kind=kind,source=src,target=target,observed=at,
                **{'from':0,'until':12},contexts=contexts or ['default','lab'],evidence_ids=[evidence])
def admit(id,relation,kind,at,evidence,outcome='ADMITTED'):
    rules={'CORRECTS':'ALLOW_CORRECTION','DISPUTES':'REGISTER_DISPUTE',
           'SUPERSEDES':'ALLOW_SUPERSESSION','ADDS_CONTEXT':'REGISTER_CONTEXT'}
    return dict(id=id,relation_id=relation,reviewer='declared-reviewer-not-authenticated',
                rule=rules[kind],observed=at,evidence_ids=[evidence],outcome=outcome)

def main_episode():
    L=make_ledger();L['evidence']=[ev('e0',0)]
    L['claims']=[claim('original','observation','sealed','A','B','T',0,'e0')]
    states=[copy.deepcopy(L)]
    L['evidence'].append(ev('e1',1))
    L['claims'].append(claim('later','observation','sealed','A','B','F',1,'e1'))
    states.append(copy.deepcopy(L))
    L['evidence'].append(ev('er2',2))
    L['links'].append(link('r-correct','CORRECTS','later','original',2,'er2'))
    states.append(copy.deepcopy(L))
    L['admissions'].append(admit('a-correct','r-correct','CORRECTS',2,'er2'))
    states.append(copy.deepcopy(L))
    return states

def full_fixture():
    L=main_episode()[-1]
    # One accepted challenge without contradictory assertion: does not refute claim.
    L['evidence']+= [ev('e3',3),ev('er4',4),ev('e5',5),ev('er6',6),ev('e7',7),ev('er8',8)]
    L['claims'].append(claim('challenge','observation','sealed','A','B','F',3,'e3'))
    L['links'].append(link('r-dispute','DISPUTES','challenge','later',4,'er4'))
    L['admissions'].append(admit('a-dispute','r-dispute','DISPUTES',4,'er4'))
    L['claims'].append(claim('policy-old','policy','transfer-permitted','A','B','T',0,'e0'))
    new_policy=claim('policy-new','policy','transfer-permitted','A','B','F',5,'e5')
    new_policy['from']=6
    L['claims'].append(new_policy)
    sup=link('r-sup','SUPERSEDES','policy-new','policy-old',6,'er6')
    sup['from']=6
    L['links'].append(sup)
    L['admissions'].append(admit('a-sup','r-sup','SUPERSEDES',6,'er6'))
    L['claims'].append(claim('extra','context','risk-label','A','B','T',7,'e7'))
    L['links'].append(link('r-context','ADDS_CONTEXT','extra','later',8,'er8',contexts=['lab']))
    L['admissions'].append(admit('a-context','r-context','ADDS_CONTEXT',8,'er8'))
    return L

ATOM={'op':'ATOM','kind':'observation','predicate':'sealed','subject':'A','object':'B'}
POLICY={'op':'ATOM','kind':'policy','predicate':'transfer-permitted','subject':'A','object':'B'}

def to_lex(expr):
    op=expr['op']
    if op=='ATOM':return ['A',expr['kind'],expr['predicate'],expr['subject'],expr['object']]
    if op=='LINK':return ['L',expr['id']]
    if op=='SCOPE':return ['S',expr['query'],expr['knowledge'],expr['context'],to_lex(expr['body'])]
    if op=='NOT':return ['N',to_lex(expr['arg'])]
    return [('&' if op=='ALL' else '|')]+[to_lex(x) for x in expr['args']]
