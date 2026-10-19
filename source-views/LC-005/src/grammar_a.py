"""Scanner parser for path-composition candidate A; retains versioned macro calls."""
import re
NAME=re.compile(r'[A-Z][A-Z0-9]*\Z')
class ParserA:
    def parse(self,source):
        if type(source) is not str or len(source)>65536:raise ValueError('source length/type')
        s=''.join(source.split());pos=0;count=0
        def call(depth):
            nonlocal pos,count
            count+=1
            if depth>192 or count>8192:raise ValueError('expression resource bound')
            beg=pos
            while pos<len(s) and s[pos].isalnum():pos+=1
            name=s[beg:pos]
            if not name or pos>=len(s) or s[pos]!='(':raise ValueError('expected function call')
            pos+=1
            if name=='R':
                args=[]
                for k in range(2):
                    beg=pos
                    while pos<len(s) and s[pos].isalnum():pos+=1
                    word=s[beg:pos]
                    if not NAME.fullmatch(word):raise ValueError('invalid endpoint')
                    args.append(word)
                    if k==0:
                        if pos>=len(s) or s[pos]!=',':raise ValueError('R comma')
                        pos+=1
                node=('R',*args)
            elif name in ('C','CHOICE'):
                a=call(depth+1)
                if pos>=len(s) or s[pos]!=',':raise ValueError('binary comma')
                pos+=1;b=call(depth+1);node=(name,a,b)
            elif name=='J':
                beg=pos
                while pos<len(s) and s[pos].isalnum():pos+=1
                pred=s[beg:pos]
                if pred not in ('P','S') or pos>=len(s) or s[pos]!='(':raise ValueError('invalid guard')
                pos+=1;beg=pos
                while pos<len(s) and s[pos].isalnum():pos+=1
                entity=s[beg:pos]
                if not NAME.fullmatch(entity) or pos>=len(s) or s[pos]!=')':raise ValueError('invalid guard entity')
                pos+=1
                if pos>=len(s) or s[pos]!=',':raise ValueError('guard comma')
                pos+=1;node=('J',(pred,entity),call(depth+1))
            elif name=='AT':
                beg=pos
                while pos<len(s) and s[pos].isdigit():pos+=1
                raw=s[beg:pos]
                if not raw or (len(raw)>1 and raw[0]=='0') or len(raw)>8:raise ValueError('invalid AT stage')
                if pos>=len(s) or s[pos]!=',':raise ValueError('AT comma')
                pos+=1;node=('AT',int(raw),call(depth+1))
            elif name in ('H1','H2'):
                args=[]
                for i in range(3):
                    beg=pos
                    while pos<len(s) and s[pos].isalnum():pos+=1
                    arg=s[beg:pos]
                    if not NAME.fullmatch(arg):raise ValueError('invalid macro argument')
                    args.append(arg)
                    if i<2:
                        if pos>=len(s) or s[pos]!=',':raise ValueError('macro comma')
                        pos+=1
                node=('MACRO',name,tuple(args))
            else:raise ValueError('unsupported descriptor '+name)
            if pos>=len(s) or s[pos]!=')':raise ValueError('unbalanced call')
            pos+=1
            return node
        tree=call(0)
        if pos!=len(s):raise ValueError('trailing syntax')
        return tree
