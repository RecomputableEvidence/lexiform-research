"""Interpreter A: recursive descent -> immutable tree -> recursive strong-Kleene evaluation.
It does not import Interpreter B or its representations.
"""
import re
import copy
from dataclasses import dataclass
from common import details, digest

TOK = re.compile(r'\s*([A-Za-z][A-Za-z0-9]*|[!&|>(),])')

@dataclass(frozen=True)
class Node:
    tag: str
    value: str = ''
    args: tuple = ()

class InterpreterA:
    def __init__(self, definitions, *, reuse=True, result_cache=True):
        self.definitions = copy.deepcopy(definitions)
        self._initial_definition_digest = digest(self.definitions)
        self._expanding = set()
        self.reuse = reuse
        self.result_cache = result_cache
        self.parsed = {}
        self.expansions = {}
        self.memo = {}
        self.stats = {'parsed':0,'definition_expansions':0,'definition_reuse_hits':0,'result_cache_hits':0}

    def _tokens(self, s):
        pos=0; tokens=[]
        while pos<len(s):
            m=TOK.match(s,pos)
            if not m:
                if s[pos:].strip()=='':
                    break
                raise ValueError(f'invalid character at {pos}')
            tokens.append(m.group(1)); pos=m.end()
        return tokens

    def parse(self, text):
        if digest(self.definitions)!=self._initial_definition_digest:
            raise ValueError("definition registry changed during frozen run")
        if self.reuse and text in self.parsed:
            return self.parsed[text]
        tokens=self._tokens(text)
        self.stats['parsed']+=1
        pos=0
        def read():
            nonlocal pos
            if pos>=len(tokens):
                raise ValueError('unexpected end')
            item=tokens[pos]; pos+=1
            return item
        def expect(want):
            item=read()
            if item!=want:
                raise ValueError(f'expected {want}, got {item}')
        def expression(depth):
            if depth>64: raise ValueError('nesting limit')
            op=read(); expect('(')
            if op in ('S','P') or re.fullmatch('G[1-9][0-9]*',op):
                name=read()
                if (not re.fullmatch('[A-Za-z][A-Za-z0-9]*',name)
                        or name in ('S','P') or re.fullmatch(r'G[1-9][0-9]*',name)):
                    raise ValueError('valid nonreserved entity required')
                expect(')')
                if op in ('S','P'):
                    return Node('atom',f'{op}({name})')
                return self._expand(op,name)
            if op=='!':
                item=expression(depth+1); expect(')')
                return Node('not',args=(item,))
            if op in ('&','|','>'):
                a=expression(depth+1); expect(','); b=expression(depth+1); expect(')')
                return Node(op,args=(a,b))
            raise ValueError('unknown operation '+op)
        tree=expression(0)
        if pos!=len(tokens): raise ValueError('trailing tokens')
        if self.reuse: self.parsed[text]=tree
        return tree

    def _expand(self, op, entity):
        key=(op,entity)
        if self.reuse and key in self.expansions:
            self.stats['definition_reuse_hits']+=1
            return self.expansions[key]
        if op not in self.definitions: raise ValueError('unknown definition version '+op)
        if key in self._expanding: raise ValueError('cyclic definition')
        self._expanding.add(key)
        try:
            self.stats['definition_expansions']+=1
            definition=self.definitions[op]['expression']
            expanded=self.parse(definition.replace('{x}',entity))
            if self.reuse: self.expansions[key]=expanded
            return expanded
        finally:
            self._expanding.remove(key)

    @staticmethod
    def _truth(tag, a, b=None):
        if tag=='not': return {'T':'F','F':'T','U':'U'}[a]
        if tag=='&': return 'F' if 'F' in (a,b) else ('T' if a==b=='T' else 'U')
        if tag=='|': return 'T' if 'T' in (a,b) else ('F' if a==b=='F' else 'U')
        if tag=='>': return InterpreterA._truth('|',InterpreterA._truth('not',a),b)
        raise ValueError(tag)

    def evaluate(self, expression, *, evidence=None, stage=0, valuation=None):
        if (evidence is None)==(valuation is None):
            raise ValueError('provide exactly one: evidence or valuation')
        tree=self.parse(expression)
        memo_key=None
        if self.result_cache:
            stamp=digest(evidence) if evidence is not None else digest(valuation)
            memo_key=(expression,stage,stamp)
            if memo_key in self.memo:
                self.stats['result_cache_hits']+=1
                return copy.deepcopy(self.memo[memo_key])
        def ev(node):
            if node.tag=='atom':
                key=node.value
                if valuation is not None: return valuation.get(key,'U'),{key}
                m=re.fullmatch(r'([SP])\(([A-Za-z][A-Za-z0-9]*)\)',key)
                return details(evidence,stage,m.group(1),m.group(2))['value'],{key}
            if node.tag=='not':
                v,k=ev(node.args[0]); return self._truth('not',v),k
            left,lk=ev(node.args[0]); right,rk=ev(node.args[1]);
            return self._truth(node.tag,left,right),lk|rk
        v,refs=ev(tree)
        out={'value':v,'atoms':sorted(refs)}
        if self.result_cache: self.memo[memo_key]=copy.deepcopy(out)
        return out

    def reconstruct(self, expression, *, evidence, stage):
        """Independent bounded interpreter-to-output projection, retaining qualifications."""
        outcome=self.evaluate(expression,evidence=evidence,stage=stage)
        support={}
        for atom in outcome['atoms']:
            m=re.fullmatch(r'([SP])\(([A-Za-z][A-Za-z0-9]*)\)',atom)
            support[atom]=details(evidence,stage,m.group(1),m.group(2))
        gaps=[atom for atom,record in support.items() if record['value']!='T']
        clauses=[f"{atom}={support[atom]['value']} ({support[atom]['reason']})" for atom in gaps]
        text=f"At stage {stage}, {expression} evaluates to {outcome['value']}."
        if clauses:
            text+=' Non-true premises: '+', '.join(clauses)+'.'
        return {'value':outcome['value'],'support':support,'text':text}
