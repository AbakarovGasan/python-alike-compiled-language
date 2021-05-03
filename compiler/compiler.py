from io import StringIO
import uuid

class InvalidToken(Exception):
    def __init__(s, *a):
        super().__init__(*a)

class InvalidSyntax(Exception):
    def __init__(s, *a):
        super().__init__(*a)

def comment(f, t='#'):
    if t!='#': return
    t=f.read(1)
    if t=='[':
        while True:
            t=f.read(1)
            if t=='':
                raise InvalidSyntax('end of multiline comment expected')
            if t==']':
                t+=f.read(1)
            if t==']#':
                return
    else:
        while t!='\n' and t!='':
            t=f.read(1)
        return
        
def get(f):
    t=f.read(1)
    while t=='#':
        comment(t)
        t=f.read(1)
    return t

def space(f):
    t=get(f)
    l=''
    while t.isspace():
        l+=t
        t=get(f)
    if t!='': f.seek(f.tell()-1)
    return l

def kernel():
    k=[False]
    def daemon(a):
        return lambda *b, **c: run(a, *b, **c) 
    def end():
        k[0]=False
    def run(a, *b, **c):
        i=k[0]
        k[0]=True
        while k[0]:
            a(*b, **c)
        k[0]=i
    class kernel:
        pass
    kernel.daemon=daemon
    kernel.run=run
    kernel.end=end
    return kernel
    
kernel=kernel()
        
class glob:
    str=type('str', (type('str'),), {})
    numhex=['0', '1', '2', '3',
     '4', '5', '6', '7', '8',
     '9', 'A', 'a', 'B', 'b', 
     'C', 'c', 'D', 'd', 'E',
     'e', 'F', 'f']
    numdec=['0', '1', '2', '3',
     '4', '5', '6', '7', '8', '9']
    numoct=['0', '1', '2', '3',
     '4', '5', '6', '7']
    numbin=['0', '1']
    spec=['+', '-', '*', '/', 
     '%', '~', '|', '&', '^', 
     '>', '<','=']
    braces=['(', ')', '[', ']', '{', '}']
    dots=['.', ',', ':']
    indents=[0]
    

def token(f):
    space(f)
    t=get(f)
    iden=''
    if t=='': return '', ''
    if (t in glob.braces):
         iden='brace'
         return t, iden
    if (t in glob.dots):
         iden='dot'
         return t, iden
    l=''
    if t=='"':
        iden='string'
        t=f.read(1)
        if t=='"':
            t=f.read(1)
            if t!='"':
                if t!='':
                    f.seek(f.tell()-1)
                return '""', iden
            l+='"""'
            v=0
            while v<3:
                t=f.read(1)
                if t=='':
                    raise InvalidSyntax('closing """  expected')
                if t=='"':
                    v+=1
                else:
                    v=0
                l+=t
            return l, iden
        else:
            l='"'
            while t!='"':
                if t=='':
                    raise InvalidSyntax('closing " expected')
                l+=t
                if t=='\\':
                    t=f.read(1)
                    l+=t
                t=f.read(1)
            l+=t
            return l, iden
    elif t.isidentifier():
        iden='word'
        while t.isidentifier() or t.isdigit():
            l+=t
            t=f.read(1)
        l=l.lower()
    elif t in glob.numdec:
        iden='number'
        k=glob.numdec
        x=10
        if t=='0':
            t=f.read(1).lower()
            if t=='b':
                x=2
                k=glob.numbin
            elif t=='x':
                x=16
                k=glob.numhex
            elif t=='o':
                x=8
                k=glob.numoct
            else:
                f.seek(f.tell()-2)
            t=f.read(1)
        if not t or t.isspace():
            raise InvalidSyntax('invalid number')
        while t!='' and not t.isspace():
            if t=='_':
                t=f.read(1)
                continue
            if not t in k:
                if t.isidentifier() and (not t in glob.spec):
                    raise InvalidSyntax('invalid number')
                else:
                    break
            l+=t
            t=f.read(1)
        if x!=10:
            l=l[2:]
        l=str(int(l, x))
    elif t in glob.spec:
        iden='special'
        while t in glob.spec:
            l+=t
            t=f.read(1)
    if t!='':
        f.seek(f.tell()-1)
    return l, iden

def __():
    global token
    __=token
    def token(f):
        l, iden=__(f)
        l=glob.str(l)
        l.iden=iden
        return l
__()

def void():
    pass


loop={}

def __():
    n=''
    c={}
    def _(b):
        nonlocal n
        nonlocal c
        c[n]=b
        
    def add(d, a):
        nonlocal n
        nonlocal c
        n=a
        c=d
        return _
    return add
add=__()

def getline(f):
    l=''
    t=f.read(1)
    h=[]
    while t!='':
        while h and t==h[-1]:
            h.pop(-1)
            l+=t
            t=f.read(1)
        if not h and t=='\n':
            break
        comment(f, t)
        if t=='"':
            f.seek(f.tell()-1)
            t=token(f)
        if t in glob.braces:
            j=glob.braces.index(t)
            if (j%2)==1:
                raise InvalidSyntax("beginning brace '"+glob.braces[j-1]+"' is expected")
            h.append(glob.braces[j+1])
        l+=t
        t=f.read(1)
    if h:
        if len(h)==1:
            raise InvalidSyntax("closing brace '"+h[-1]+"' is expected")
        else:
            raise InvalidSyntax("closing braces "+repr(h[1:])+" are expected")
    return l

def token_list(f, j=0):
    j-=len(space(f))
    if j:
        raise InvalidSyntax("unexpected indent")
    l=StringIO(getline(f))
    k=token(l)
    j=[]
    while k!='':
        j.append(k)
        k=token(l)
    return j

class table:
    words={}
    operators={}
    vars={}
    types={'int': uuid.uuid4(), 
        'string': uuid.uuid4(),
    }

def _():
    class c:
        int=table.types['int']
        str=table.types['string']
    class _l():
       def __init__(s, l):
           s.l=l
           s.i=0
       def __iter__(s):
           return s
       def get(s):
           try:
              r=s.l[s.i]
           except Exception as e:
              return None
           s.i+=1
           return r
       __next__=get 
    
    global get_type, abstract_tree 
    
    def get_type(a):
        if a.iden=='number':
            return c.int
        if a.iden=='string':
            return c.str
        if a.iden=='word':
            return table.vars[a].type
 
    
    def _a1(l, b=None, k=None):
   #     print('b:', b)
        a=l.get()
   #     print(a)
        
        if a == k:
            return b
        elif not is_key(a):
            if b==None:
                if is_brace(a):
                    a=_a1(l, None, refl(a))
                return _a1(l, a, k)
            else:
                raise Exception("kill youself, ellay escaban bustamante")
        else:
            y=[]
            while True:
                w, x, z = _a3(l, _a2(l))
                if not z:
                    y.append(b)
                    y.append(a)
                    y.append(w)
                else:
                    y.append(w)
                    y.append(a)
                    y.append(b)
                a = x
                if a == k:
                    return y
                if is_key(a):
                    b=y
                    y=[]
                    continue
                raise Exception("kill youself, ellay escaban bustamante")
    
    def _a2(l, b=None):
        a=l.get()
        if not is_key(a):
            if is_brace(a):
                return _a1(l, None, refl(a))
            return a
        c=[]
        y=c
        y.append(None)
        y.append(a)
        a = l.get()
        while is_key(a):
           k = []
           y.append(k)
           y = k
           y.append(None)
           y.append(a)
           a=l.get()
        if is_brace(a): a = _a1(l, None, refl(a))
        y.append(a)
        return c
                
    def _a3(l, b=None, c=2):
        a=l.get()
        push = False
        while prior(a)==c:
            b = [b]
            b.append(a)
            x = _a2(l)
            if x == None:
                raise Exception("kill youself, ellay escaban bustamante")
            b.append(x)
            push = True
            a = l.get()
        return b, a, push
    
    def prior(a):
        if a in ['/', '*']:
            return 2
        else:
            return 1
            
    def refl(a):
        return glob.braces[glob.braces.index(a)+1]
    
    def is_key(a):
        return a.iden=='special'
        
    def is_brace(a):
        return a.iden=='brace'
    
    def abstract_tree(l):
        #create abstract_tree from an token_list
        return _a1(_l(l))
_()

j="- 9 + 902"
q=StringIO(j)

n=abstract_tree(token_list(q))
print(n)

import code
code.InteractiveConsole(globals()).interact()



