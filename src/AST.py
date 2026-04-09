class Node(object):
    pass


class IntNum(Node):
    def __init__(self, line=None, value=None):
        self.line = line
        self.value = value

class FloatNum(Node):
    def __init__(self, line=None, value=None):
        self.line = line
        self.value = value

class Vector(Node):
    def __init__(self, line=None, elements=None):
        self.line = line
        self.elements = elements

class Variable(Node):
    def __init__(self, line=None, name=None):
        self.line = line
        self.name = name

class String(Node):
    def __init__(self, line=None, value=None):
        self.line = line
        self.value = value

class BinExpr(Node):
    def __init__(self, line=None, op=None, left=None, right=None):
        self.line = line
        self.op = op
        self.left = left
        self.right = right

class Program(Node):
    def __init__(self, line=None, statements=None):
        self.line = line
        self.statements = statements or []

class ExprStmt(Node):
    def __init__(self, line=None, expr=None):
        self.line = line
        self.expr = expr

class For(Node):
    def __init__(self, line=None, var=None, start=None, end=None, body=None):
        self.line = line
        self.var = var
        self.start = start
        self.end = end
        self.body = body

class While(Node):
    def __init__(self, line=None, condition=None, body=None):
        self.line = line
        self.condition = condition
        self.body = body

class If(Node):
    def __init__(self, line=None, condition=None, then_block=None, else_block=None):
        self.line = line
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class Block(Node):
    def __init__(self, line=None, statements=None):
        self.line = line
        self.statements = statements or []

class Continue(Node):
    def __init__(self, line=None):
        self.line = line

class Break(Node):
    def __init__(self, line=None):
        self.line = line

class Return(Node):
    def __init__(self, line=None, expr=None):
        self.line = line
        self.expr = expr

class Print(Node):
    def __init__(self, line=None, expr_list=None):
        self.line = line
        self.expr_list = expr_list

class AssignIndex(Node):
    def __init__(self, line=None, target=None, value=None):
        self.line = line
        self.target = target
        self.value = value

class Assign(Node):
    def __init__(self, line=None, target=None, value=None):
        self.line = line
        self.target = target
        self.value = value

class Slice(Node):
    def __init__(self, line=None, start=None, step=None, end=None):
        self.line = line
        self.start = start
        self.step = step
        self.end = end

class Index(Node):
    def __init__(self, line=None, collection=None, indices=None):
        self.line = line
        self.collection = collection
        self.indices = indices

class Transpose(Node):
    def __init__(self, line=None, expr=None):
        self.line = line
        self.expr = expr

class BuiltinCall(Node):
    def __init__(self, line=None, name=None, arg=None):
        self.line = line
        self.name = name
        self.arg = arg

class Matrix(Node):
    def __init__(self, line=None, rows=None):
        self.line = line
        self.rows = rows

class UnExpr(Node):
    def __init__(self, line=None, op=None, expr=None):
        self.line = line
        self.op = op
        self.expr = expr



class Error(Node):
    def __init__(self, line=None, message=None):
        self.line = line
        self.message = message
