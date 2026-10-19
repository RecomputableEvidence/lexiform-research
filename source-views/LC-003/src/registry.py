"""Explicit, sealed lexical identities and expansion lineage."""
import copy
import re
from evidence import sha

VALID_EXPR = re.compile(r'^[A-Za-z0-9(), \t\r\n]+$')
ENTITY = re.compile(r'[A-Z][A-Z0-9]*\Z')
MACROS = re.compile(r'\b(H[12])\(([A-Z][A-Z0-9]*),([A-Z][A-Z0-9]*),([A-Z][A-Z0-9]*)\)')

class FrozenDefinitions:
    def __init__(self, definitions):
        if type(definitions) is not dict or set(definitions)!={'H1','H2'}:
            raise ValueError('only H1/H2 accepted in this bounded experiment')
        defs=copy.deepcopy(definitions)
        for name,entry in defs.items():
            if type(entry) is not dict or set(entry)!={'version','parameters','expression'}:
                raise ValueError('definition schema mismatch')
            if type(entry['version']) is not int or entry['version'] < 1:
                raise ValueError('macro version must be positive int')
            if entry['parameters']!=['a','b','c']:
                raise ValueError('invalid macro params')
            if type(entry['expression']) is not str or not entry['expression']:
                raise ValueError('missing macro expression')
            if not VALID_EXPR.fullmatch(entry['expression'].replace('{a}','A').replace('{b}','B').replace('{c}','C')):
                raise ValueError('invalid macro definition characters')
            published={
                'H1':(1,'C(R({a},{b}),R({b},{c}))'),
                'H2':(2,'J(P({b}),C(R({a},{b}),R({b},{c})))')
            }
            if (entry['version'],entry['expression']) != published[name]:
                raise ValueError('macro version/content binding differs from admitted LC-EXP-002 definition')
        self._defs=defs
        self.digest=sha({'schema':'LC-EXP-003-REGISTRY-1.0.0','entries':defs})
    def _check_seal(self):
        if sha({'schema':'LC-EXP-003-REGISTRY-1.0.0','entries':self._defs}) != self.digest:
            raise ValueError('registry changed after binding')
    def get_definitions(self):
        self._check_seal()
        return copy.deepcopy(self._defs)

    def invocation_lineage(self, source):
        self._check_seal()
        # Deliberately bounded: H1/H2 accept literal parameters, and their definitions
        # are recursively scanned without promoting expanded form into historical source.
        lines=[]
        def walk(expr, ancestor, depth):
            if depth>16:raise ValueError('macro recursion bound')
            for m in MACROS.finditer(expr):
                name=m.group(1); args=m.group(2,3,4)
                defn=self._defs[name]
                expanded=defn['expression']
                for key,val in zip(('a','b','c'),args):expanded=expanded.replace('{'+key+'}',val)
                lines.append({'name':name,'version':defn['version'],'arguments':list(args),
                              'invocation':m.group(0),'source_span':[m.start(),m.end()], 'definition_sha256':sha(defn),
                              'expanded':expanded, 'parent':ancestor})
                if any(line['name']==name and line['parent']==ancestor for line in lines[:-1]) and depth>0:
                    # Not a general proof of cyclic expansion: actual parsers enforce that.
                    pass
                if name in ancestor:raise ValueError('cyclic macro')
                walk(expanded,ancestor+(name,),depth+1)
        walk(source,(),0)
        return lines
