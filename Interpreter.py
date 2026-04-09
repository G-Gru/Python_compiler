
import AST
import SymbolTable
from Memory import *
from Exceptions import  *
from visit import *
import sys

sys.setrecursionlimit(10000)

def _truthy(value):
    return bool(value)


def _elementwise(a, b, op):
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            raise RuntimeError("dimension mismatch")
        return [_elementwise(x, y, op) for x, y in zip(a, b)]
    if isinstance(a, list) or isinstance(b, list):
        raise RuntimeError("dimension mismatch")
    return op(a, b)


class Interpreter(object):
    def __init__(self):
        self.globalMemory = MemoryStack(Memory("global"))

    @on("node")
    def visit(self, node):
        pass

    @when(AST.Program)
    def visit(self, node):
        result = None
        for stmt in node.statements:
            result = self.visit(stmt)
        return result

    @when(AST.Block)
    def visit(self, node):
        self.globalMemory.push(Memory("block"))
        try:
            result = None
            for stmt in node.statements:
                result = self.visit(stmt)
            return result
        finally:
            self.globalMemory.pop()

    @when(AST.IntNum)
    def visit(self, node):
        return node.value

    @when(AST.FloatNum)
    def visit(self, node):
        return node.value

    @when(AST.String)
    def visit(self, node):
        return node.value

    @when(AST.Vector)
    def visit(self, node):
        return [self.visit(e) for e in node.elements]

    @when(AST.Matrix)
    def visit(self, node):
        return [[self.visit(e) for e in row] for row in node.rows]

    @when(AST.Variable)
    def visit(self, node):
        return self.globalMemory.get(node.name)

    @when(AST.AssignIndex)
    def visit(self, node):
        value = self.visit(node.value)
        if isinstance(node.target, AST.Variable):
            self.globalMemory.set(node.target.name, value)
            return value

        if isinstance(node.target, AST.Index):
            base = self.visit(node.target.collection)
            indices = node.target.indices

            if not isinstance(indices, list):
                raise RuntimeError("invalid index list")

            if len(indices) == 1:
                i = self.visit(indices[0])
                base[i] = value
                return value
            if len(indices) == 2:
                i = self.visit(indices[0])
                j = self.visit(indices[1])
                base[i][j] = value
                return value

        raise RuntimeError("unsupported assignment target")

    @when(AST.Index)
    def visit(self, node):
        base = self.visit(node.collection)

        idx = node.indices

        if isinstance(idx, list):
            if len(idx) == 1:
                i = int(self.visit(idx[0]))
                return base[i]
            if len(idx) == 2:
                i = int(self.visit(idx[0]))
                j = int(self.visit(idx[1]))
                return base[i][j]

        raise RuntimeError("unsupported index form")

    @when(AST.Print)
    def visit(self, node):
        for expr in node.expr_list:
            val = self.visit(expr)
            print(val)
        return None

    @when(AST.Break)
    def visit(self, node):
        raise BreakException()

    @when(AST.Continue)
    def visit(self, node):
        raise ContinueException()

    @when(AST.Return)
    def visit(self, node):
        val = self.visit(node.expr) if node.expr is not None else None
        raise ReturnValueException(val)

    @when(AST.If)
    def visit(self, node):
        cond = self.visit(node.condition)
        if _truthy(cond):
            return self.visit(node.then_block)
        if node.else_block is not None:
            return self.visit(node.else_block)
        return None

    @when(AST.While)
    def visit(self, node):
        result = None
        while _truthy(self.visit(node.condition)):
            try:
                result = self.visit(node.body)
            except ContinueException:
                continue
            except BreakException:
                break
        return result

    @when(AST.For)
    def visit(self, node):
        start = self.visit(node.start)
        end = self.visit(node.end)
        result = None
        for i in range(int(start), int(end)):
            self.globalMemory.set(node.var.name, i)
            try:
                result = self.visit(node.body)
            except ContinueException:
                continue
            except BreakException:
                break
        return result

    @when(AST.UnExpr)
    def visit(self, node):
        v = self.visit(node.expr)
        if node.op == "+":
            return +v
        if node.op == "-":
            return -v
        raise RuntimeError("unknown unary operator")

    @when(AST.Transpose)
    def visit(self, node):
        v = self.visit(node.expr)
        if isinstance(v, list) and v and isinstance(v[0], list):
            return [list(row) for row in zip(*v)]
        return v

    @when(AST.BuiltinCall)
    def visit(self, node):
        n = int(self.visit(node.arg))

        if node.name.upper() == "ZEROS":
            return [[0 for _ in range(n)] for _ in range(n)]
        if node.name.upper() == "ONES":
            return [[1 for _ in range(n)] for _ in range(n)]
        if node.name.upper() == "EYE":
            m = [[0 for _ in range(n)] for _ in range(n)]
            for i in range(n):
                m[i][i] = 1
            return m

        raise RuntimeError("unknown builtin")

    @when(AST.BinExpr)
    def visit(self, node):
        a = self.visit(node.left)
        b = self.visit(node.right)
        op = node.op

        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return a / b

        if op == "==":
            return a == b
        if op == "!=":
            return a != b
        if op == "<":
            return a < b
        if op == ">":
            return a > b
        if op == "<=":
            return a <= b
        if op == ">=":
            return a >= b

        if op == ".+":
            return _elementwise(a, b, lambda x, y: x + y)
        if op == ".-":
            return _elementwise(a, b, lambda x, y: x - y)
        if op == ".*":
            return _elementwise(a, b, lambda x, y: x * y)
        if op == "./":
            return _elementwise(a, b, lambda x, y: x / y)

        raise RuntimeError("unknown binary operator")
