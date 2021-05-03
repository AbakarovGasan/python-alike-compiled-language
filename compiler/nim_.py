from io import StringIO
import uuid

class InvalidToken(Exception):
    def __init__(s, *a):
        super().__init__(*a)

class InvalidSyntax(Exception):
    def __init__(s, *a):
        super().__init__(*a)
        
#this function checks stream for comment
#and returns next char after comment if comment here
#else returns t
def pass_comment(f, t):
    if t!='#':
        return t
    else:
        t = f.read(1)
        if t!='[':
            while t!='\n':
                t = f.read(1)
                if t=='':
                    raise InvalidSyntax("newline is expected")
            return f.read(1)
        else:
            while True:
                t = f.read(1)
                if t=='':
                    raise InvalidSyntax("]# is expected")
                if t==']':
                    t = f.read(1)
                    if t=='#':
                        break
            return f.read(1)
            

        
