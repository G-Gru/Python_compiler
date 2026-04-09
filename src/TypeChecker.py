import AST
from SymbolTable import SymbolTable, VariableSymbol


class NodeVisitor(object):
    def visit(self, node):
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        if isinstance(node, list):
            for elem in node:
                self.visit(elem)
        else:
            for attr in getattr(node, "__dict__", {}).values():
                if isinstance(attr, AST.Node):
                    self.visit(attr)
                elif isinstance(attr, list):
                    for item in attr:
                        if isinstance(item, AST.Node):
                            self.visit(item)


class TypeInfo:
    # kind: "scalar" | "vector" | "matrix" | "string" | "unknown"
    # shape: () | (n,) | (r,c)
    def __init__(self, kind="unknown", shape=None):
        self.kind = kind
        self.shape = shape

    def __repr__(self):
        return f"TypeInfo({self.kind}, {self.shape})"


def is_int_scalar(t: TypeInfo) -> bool:
    return t.kind == "scalar"


def is_numeric(t: TypeInfo) -> bool:
    return t.kind in ("scalar", "vector", "matrix")


def same_shape(a: TypeInfo, b: TypeInfo) -> bool:
    return a.shape == b.shape and a.kind == b.kind


class TypeChecker(NodeVisitor):
    def __init__(self):
        self.errors = []
        self.symtab = SymbolTable(None, "global")
        self.loop_depth = 0

    def error(self, node, msg):
        line = getattr(node, "line", None)
        loc = f"line={line}" if line is not None else "line=?"
        self.errors.append(f"{loc}: {msg}")
        print(self.errors[-1])

    # ---------- program / blocks ----------

    def visit_Program(self, node: AST.Program):
        for s in node.statements:
            self.visit(s)
        return TypeInfo("unknown")

    def visit_Block(self, node: AST.Block):
        old = self.symtab
        self.symtab = self.symtab.pushScope("block")
        for s in node.statements:
            self.visit(s)
        self.symtab = old
        return TypeInfo("unknown")

    # ---------- literals / variables ----------

    def visit_IntNum(self, node: AST.IntNum):
        return TypeInfo("scalar", ())

    def visit_FloatNum(self, node: AST.FloatNum):
        return TypeInfo("scalar", ())

    def visit_String(self, node: AST.String):
        return TypeInfo("string", None)

    def visit_Variable(self, node: AST.Variable):
        sym = self.symtab.get(node.name)
        if sym is None:
            return TypeInfo("unknown", None)
        return sym.type

    # ---------- statements ----------

    def visit_Print(self, node: AST.Print):
        self.visit(node.expr_list)
        return TypeInfo("unknown")

    def visit_Return(self, node: AST.Return):
        if node.expr is not None:
            self.visit(node.expr)
        return TypeInfo("unknown")

    def visit_Break(self, node: AST.Break):
        if self.loop_depth <= 0:
            self.error(node, "`break` used outside of a loop")
        return TypeInfo("unknown")

    def visit_Continue(self, node: AST.Continue):
        if self.loop_depth <= 0:
            self.error(node, "`continue` used outside of a loop")
        return TypeInfo("unknown")

    def visit_If(self, node: AST.If):
        self.visit(node.condition)
        self.visit(node.then_block)
        if node.else_block is not None:
            self.visit(node.else_block)
        return TypeInfo("unknown")

    def visit_While(self, node: AST.While):
        self.visit(node.condition)
        self.loop_depth += 1
        self.visit(node.body)
        self.loop_depth -= 1
        return TypeInfo("unknown")

    def visit_For(self, node: AST.For):
        t0 = self.visit(node.start)
        t1 = self.visit(node.end)
        if t0.kind != "scalar" or t1.kind != "scalar":
            self.error(node, "`for` range bounds must be scalar")
        # iterator becomes scalar
        self.symtab.put(node.var.name, VariableSymbol(node.var.name, TypeInfo("scalar", ())))
        self.loop_depth += 1
        self.visit(node.body)
        self.loop_depth -= 1
        return TypeInfo("unknown")

    def visit_Assign(self, node: AST.Assign):
        tv = self.visit(node.value)
        if isinstance(node.target, AST.Variable):
            self.symtab.put(node.target.name, VariableSymbol(node.target.name, tv))
        else:
            self.visit(node.target)
        return tv

    def visit_AssignIndex(self, node: AST.AssignIndex):
        tv = self.visit(node.value)
        if isinstance(node.target, AST.Variable):
            self.symtab.put(node.target.name, VariableSymbol(node.target.name, tv))

        self.visit(node.target)

        return tv

    # ---------- unary / transpose ----------

    def visit_UnExpr(self, node: AST.UnExpr):
        t = self.visit(node.expr)
        if t.kind not in ("scalar", "vector", "matrix"):
            self.error(node, f"unary `{node.op}` expects numeric operand")
        return t

    def visit_Transpose(self, node: AST.Transpose):
        t = self.visit(node.expr)
        if t.kind == "matrix" and t.shape and len(t.shape) == 2:
            r, c = t.shape
            return TypeInfo("matrix", (c, r))
        if t.kind == "vector" and t.shape and len(t.shape) == 1:
            # treat transpose of vector as vector (simplification)
            return t
        if t.kind == "scalar":
            return t
        self.error(node, "transpose applied to non-numeric value or uninitialized variable")
        return TypeInfo("unknown", None)

    # ---------- matrices / builtins ----------

    def visit_Matrix(self, node: AST.Matrix):
        if not node.rows:
            self.error(node, "empty matrix literal")
            return TypeInfo("matrix", (0, 0))

        row_lens = []
        for row in node.rows:
            row_lens.append(len(row))
            for elem in row:
                et = self.visit(elem)
                if et.kind != "scalar":
                    self.error(elem, "matrix elements must be scalar")
        if len(set(row_lens)) != 1:
            self.error(node, "matrix initialized with rows of different lengths")
            cols = max(row_lens) if row_lens else 0
        else:
            cols = row_lens[0]
        rows = len(node.rows)
        if rows == 1 and cols == 1:
            return TypeInfo("scalar", ())
        return TypeInfo("matrix", (rows, cols))

    def visit_BuiltinCall(self, node: AST.BuiltinCall):
        arg_t = self.visit(node.arg)
        if arg_t.kind != "scalar":
            self.error(node, f"`{node.name}` expects scalar argument")
        if isinstance(arg_t, AST.IntNum):
            n = node.arg.value
            return TypeInfo("matrix", (n, n))
        return TypeInfo("matrix", None)  

    # ---------- indexing ----------

    def visit_Slice(self, node: AST.Slice):
        self.visit(node.start)
        self.visit(node.step)
        self.visit(node.end)
        return TypeInfo("unknown", None)

    def visit_Index(self, node: AST.Index):
        base_t = self.visit(node.collection)

        def const_int(expr):
            return expr.value if isinstance(expr, AST.IntNum) else None

        if base_t.kind == "vector" and base_t.shape and len(base_t.shape) == 1:
            n = base_t.shape[0]
            if len(node.indices) != 1:
                self.error(node, "vector expects exactly 1 index")
                return TypeInfo("unknown", None)
            idx0 = node.indices[0]
            if isinstance(idx0, AST.IndexItem):
                k = const_int(idx0.expr)
                if k is not None and (k < 0 or k >= n):
                    self.error(idx0, "index out of range for vector")
            return TypeInfo("scalar", ())
        if base_t.kind == "matrix" and base_t.shape and len(base_t.shape) == 2:
            r, c = base_t.shape
            if len(node.indices) == 1:
                idx0 = node.indices[0]
                if isinstance(idx0, AST.IndexItem):
                    k = const_int(idx0.expr)
                    if k is not None and (k < 0 or k >= r):
                        self.error(idx0, "row index out of range for matrix")
                return TypeInfo("vector", (c,))
            if len(node.indices) == 2:
                i0, i1 = node.indices[0], node.indices[1]
                if isinstance(i0, AST.IndexItem):
                    k0 = const_int(i0.expr)
                    if k0 is not None and (k0 < 0 or k0 >= r):
                        self.error(i0, "row index out of range for matrix")
                if isinstance(i1, AST.IndexItem):
                    k1 = const_int(i1.expr)
                    if k1 is not None and (k1 < 0 or k1 >= c):
                        self.error(i1, "column index out of range for matrix")
                return TypeInfo("scalar", ())
            self.error(node, "matrix expects 1 or 2 indices")
            return TypeInfo("unknown", None)
        elif base_t.kind == "matrix" and base_t.shape == None:
            print("Unable to check matrix size, ignoring the error to interpret")
            return TypeInfo("scalar", None)

        # unknown base \- still visit indices for more errors
        for idx in node.indices:
            self.visit(idx)
        self.error(node, "indexing applied to non-indexable value")
        return TypeInfo("unknown", None)

    # ---------- binary ops ----------

    def visit_BinExpr(self, node: AST.BinExpr):
        t1 = self.visit(node.left)
        t2 = self.visit(node.right)
        op = node.op

        if t1 is None or t2 is None:
            self.error(node, f"Cannot type-check binary operator `{getattr(node, 'op', '?')}`: operand has no type")
            return TypeInfo("unknown", None)

        # comparisons
        if op in ("==", "!=", "<", ">", "<=", ">="):
            if not is_numeric(t1) or not is_numeric(t2):
                self.error(node, f"operator `{op}` expects numeric operands")
            elif t1.kind != t2.kind or t1.shape != t2.shape:
                self.error(node, f"operator `{op}` applied to incompatible shapes")
            return TypeInfo("scalar", ())

        # elementwise ops
        if op in (".+", ".-", ".*", "./"):
            if t1.kind != t2.kind or t1.shape != t2.shape:
                self.error(node, f"operator `{op}` requires same dimensions")
                return TypeInfo("unknown", None)
            if not is_numeric(t1) or not is_numeric(t2):
                self.error(node, f"operator `{op}` expects numeric operands and for both variables to be initialized")
                return TypeInfo("unknown", None)
            return t1

        # scalar arithmetic
        if op in ("+", "-"):
            if t1.kind == "scalar" and t2.kind == "scalar":
                return TypeInfo("scalar", ())
            # disallow scalar\+matrix etc. (as required)
            if t1.kind != "scalar" or t2.kind != "scalar":
                self.error(node, f"operator `{op}` supports only scalars (use dot operators for arrays)")
                return TypeInfo("unknown", None)

        if op == "/":
            if t1.kind == "scalar" and t2.kind == "scalar":
                return TypeInfo("scalar", ())
            self.error(node, "operator `/` supports only scalars")
            return TypeInfo("unknown", None)

        if op == "*":
            # scalar\*scalar
            if t1.kind == "scalar" and t2.kind == "scalar":
                return TypeInfo("scalar", ())
            # matrix multiplication rules
            if t1.kind == "matrix" and t2.kind == "matrix" and t1.shape and t2.shape:
                r1, c1 = t1.shape
                r2, c2 = t2.shape
                if c1 != r2:
                    self.error(node, "matrix multiplication dimensions mismatch")
                    return TypeInfo("matrix", None)
                return TypeInfo("matrix", (r1, c2))
            if t1.kind == "matrix" and t2.kind == "vector" and t1.shape and t2.shape:
                r1, c1 = t1.shape
                (n,) = t2.shape
                if c1 != n:
                    self.error(node, "matrix-vector multiplication dimensions mismatch")
                    return TypeInfo("vector", None)
                return TypeInfo("vector", (r1,))
            if t1.kind == "vector" and t2.kind == "matrix" and t1.shape and t2.shape:
                (n,) = t1.shape
                r2, c2 = t2.shape
                if n != r2:
                    self.error(node, "vector-matrix multiplication dimensions mismatch")
                    return TypeInfo("vector", None)
                return TypeInfo("vector", (c2,))
            if t1.kind == "string" and t2.kind == "scalar":
                return TypeInfo("string", ())
            self.error(node, "operator `*` used with incompatible operand kinds")
            return TypeInfo("unknown", None)

        # fallback
        self.error(node, f"unknown binary operator `{op}`")
        return TypeInfo("unknown", None)
