"""Separate lexer/token-stream parser for the conventional typed control."""
import re
TOK=re.compile(r'[A-Za-z][A-Za-z0-9]*|\d+|[(),]')
NAME=re.compile(r'[A-Z][A-Z0-9]*\Z')
class ParserB:
    def parse(self,src):
        if type(src) is not str or len(src)>65536:raise ValueError('invalid expression size')
        cleaned=''.join(src.split());tokens=TOK.findall(cleaned)
        if ''.join(tokens)!=cleaned:raise ValueError('bad token')
        # Iterative function frames, independent of ParserA's nested scanner.
        stack=[];done=None
        for index,token in enumerate(tokens):
            if token=='(':
                if not stack or stack[-1]['mode']!='name':raise ValueError('stray open')
                stack[-1]['mode']='args'
            elif token==',':
                if not stack or stack[-1]['mode']!='args':raise ValueError('stray comma')
                if not stack[-1]['args'] or stack[-1]['need']:raise ValueError('missing argument')
                stack[-1]['need']=True
            elif token==')':
                if not stack or stack[-1]['mode']!='args' or stack[-1]['need']:raise ValueError('unbalanced close')
                f=stack.pop();op=f['name'];args=f['args']
                if op=='R' and len(args)==2 and all(type(x) is str and NAME.fullmatch(x) for x in args): node=('R',*args)
                elif op in ('C','CHOICE') and len(args)==2 and all(type(x) is tuple for x in args):node=(op,*args)
                elif op in ('P','S') and len(args)==1 and type(args[0]) is str and NAME.fullmatch(args[0]):node=(op,args[0])
                elif op=='J' and len(args)==2 and type(args[0]) is tuple and args[0][0] in ('P','S') and type(args[1]) is tuple:node=('J',args[0],args[1])
                elif op=='AT' and len(args)==2 and type(args[0]) is str and args[0].isdigit() and not (len(args[0])>1 and args[0][0]=='0') and len(args[0])<=8 and type(args[1]) is tuple:node=('AT',int(args[0]),args[1])
                elif op in ('H1','H2') and len(args)==3 and all(type(x) is str and NAME.fullmatch(x) for x in args):node=('MACRO',op,tuple(args))
                else:raise ValueError('invalid operator/arity')
                if stack:
                    parent=stack[-1]
                    if parent['mode']!='args' or not parent['need']:raise ValueError('missing delimiter')
                    parent['args'].append(node);parent['need']=False
                else:
                    if done is not None:raise ValueError('trailing call')
                    done=node
            elif stack and stack[-1]['mode']=='name':
                raise ValueError('missing opening parenthesis')
            elif not stack or stack[-1]['mode']=='args':
                if stack and not stack[-1]['need']:raise ValueError('missing comma')
                # Function name iff followed by '('; disambiguation from atoms
                # occurs by pending name frame which may be folded into parent.
                if token in ('R','C','CHOICE','J','AT','H1','H2','P','S') and index+1<len(tokens) and tokens[index+1]=='(':
                    stack.append({'name':token,'mode':'name','args':[],'need':True})
                else:
                    if not stack:raise ValueError('expected function')
                    stack[-1]['args'].append(token);stack[-1]['need']=False
            else:raise ValueError('unexpected token')
        if stack or done is None:raise ValueError('incomplete expression')
        return done
