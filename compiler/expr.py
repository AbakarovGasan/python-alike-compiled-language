import ast

def recurse(node):
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Mult) or isinstance(node.op, ast.Div):
            print('(', end='')
        recurse(node.left)
        recurse(node.op)
        recurse(node.right)
        if isinstance(node.op, ast.Mult) or isinstance(node.op, ast.Div):
            print(')', end='')
    elif isinstance(node, ast.Add):
        print('+', end='')
    elif isinstance(node, ast.Sub):
        print('-', end='')
    elif isinstance(node, ast.Mult):
        print('*', end='')
    elif isinstance(node, ast.Div):
        print('/', end='')
    elif isinstance(node, ast.Num):
        print(node.n, end='')
    else:
        for child in ast.iter_child_nodes(node):
            recurse(child)


def search_expr(node):
    returns = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.Expr):
            return child
        returns.append(search_expr(child))
    for ret in returns:
        if isinstance(ret, ast.Expr):
            return ret
    return None


formula = '4+5*7/2'

a = ast.parse(formula)

expr = search_expr(a)
if expr is not None:
    recurse(expr)
print()
