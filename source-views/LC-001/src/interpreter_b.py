"""Interpreter B: explicit frame-stack parser -> postfix instructions -> VM.
No imports of Interpreter A, no shared AST/parser/reasoning functions.
"""
import re
from common import details

class InterpreterB:
    def __init__(self, definitions):
        self.definitions = definitions

    def compile(self, text, depth=0):
        if depth>16: raise ValueError('macro cycle / nesting limit')
        tokens=[]; pos=0
        while pos<len(text):
            found=re.match(r'\s*([A-Za-z][A-Za-z0-9]*|[!&|>(),])',text[pos:])
            if found is None:
                if text[pos:].strip()=='': break
                raise ValueError('unrecognized text')
            tokens.append(found.group(1)); pos+=found.end()
        stack=[]; output=None; i=0
        def deliver(value):
            nonlocal output
            if stack:
                frame=stack[-1]
                if not frame['needs_arg']: raise ValueError('missing comma')
                frame['args'].append(value)
                frame['needs_arg']=False
            else:
                if output is not None: raise ValueError('multiple expressions')
                output=value
        while i<len(tokens):
            t=tokens[i]
            if t in ('S','P','!','&','|','>') or re.fullmatch(r'G[1-9][0-9]*',t):
                if i+1>=len(tokens) or tokens[i+1]!='(': raise ValueError('expected opening parenthesis')
                if stack and not stack[-1]['needs_arg']: raise ValueError('operator in place of comma')
                stack.append({'operator':t,'args':[],'needs_arg':True}); i+=2
                if len(stack)>64: raise ValueError('too deeply nested')
                continue
            if t==',':
                if not stack or stack[-1]['needs_arg']: raise ValueError('unexpected comma')
                stack[-1]['needs_arg']=True; i+=1; continue
            if t==')':
                if not stack: raise ValueError('unmatched close')
                frame=stack.pop()
                if frame['needs_arg']: raise ValueError('empty argument')
                op=frame['operator']; args=frame['args']
                if op in ('S','P') or re.fullmatch(r'G[1-9][0-9]*',op):
                    if len(args)!=1 or args[0][0]!='name': raise ValueError('wrong entity arguments')
                    entity=args[0][1]
                    if op in ('S','P'):
                        program=[('load',op,entity)]
                    else:
                        if op not in self.definitions: raise ValueError('missing definition')
                        source=self.definitions[op]['expression'].replace('{x}',entity)
                        program=self.compile(source,depth+1)
                else:
                    nargs=1 if op=='!' else 2
                    if len(args)!=nargs or any(a[0]!='program' for a in args):
                        raise ValueError('invalid operator arity')
                    program=[]
                    for _,commands in args: program.extend(commands)
                    program.append(('apply',op))
                deliver(('program',program))
                i+=1; continue
            if re.fullmatch('[A-Za-z][A-Za-z0-9]*',t):
                if not stack or not stack[-1]['needs_arg']:
                    raise ValueError('unexpected identifier')
                deliver(('name',t)); i+=1; continue
            raise ValueError('invalid token '+t)
        if stack or output is None or output[0]!='program': raise ValueError('incomplete expression')
        return output[1]

    @staticmethod
    def _operator(op,a,b=None):
        # T=1, U=0, F=-1. Independent three-valued implementation.
        if op=='!': return -a
        if op=='&': return min(a,b)
        if op=='|': return max(a,b)
        if op=='>': return max(-a,b)
        raise ValueError('undefined opcode')

    def evaluate(self, expr, *, evidence=None, stage=0, valuation=None):
        if (evidence is None)==(valuation is None): raise ValueError('provide evidence xor valuation')
        program=self.compile(expr)
        stack=[]
        for instruction in program:
            if instruction[0]=='load':
                _,p,entity=instruction
                atom=f'{p}({entity})'
                text=valuation.get(atom,'U') if valuation is not None else details(evidence,stage,p,entity)['value']
                if text not in ('T','F','U'): raise ValueError('invalid truth value')
                stack.append(({'T':1,'F':-1,'U':0}[text],{atom}))
            else:
                op=instruction[1]
                if op=='!':
                    left,atoms=stack.pop()
                    stack.append((self._operator(op,left),atoms))
                else:
                    right,r_refs=stack.pop(); left,l_refs=stack.pop()
                    stack.append((self._operator(op,left,right),l_refs|r_refs))
        if len(stack)!=1: raise ValueError('invalid instruction stack')
        value,atoms=stack[0]
        return {'value':{1:'T',0:'U',-1:'F'}[value], 'atoms':sorted(atoms)}

    def reconstruct(self, expression, *, evidence, stage):
        """Separately authored reconstruction from postfix VM observations."""
        evaluated=self.evaluate(expression,evidence=evidence,stage=stage)
        rows={}
        for atom in evaluated['atoms']:
            tokens=atom.replace(')','').split('(')
            rows[atom]=details(evidence,stage,tokens[0],tokens[1])
        unusual=[key+':'+entry['value']+'/'+entry['reason']
                 for key,entry in sorted(rows.items()) if entry['value']!='T']
        explanation='; '.join(unusual) if unusual else 'all referenced atoms are true'
        text=f"{expression} @ t{stage} => {evaluated['value']} [{explanation}]"
        return {'value':evaluated['value'],'support':rows,'text':text}
