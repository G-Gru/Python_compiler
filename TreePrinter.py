import AST

def addToClass(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return func
    return decorator


class TreePrinter:

    @addToClass(AST.Node)
    def printTree(self, indent=0):
        raise Exception("printTree not defined in class " + self.__class__.__name__)

    # ---------- literals ----------

    @addToClass(AST.IntNum)
    def printTree(self, indent=0):
        print("|  " * indent + str(self.value))

    @addToClass(AST.FloatNum)
    def printTree(self, indent=0):
        print("|  " * indent + str(self.value))

    @addToClass(AST.String)
    def printTree(self, indent=0):
        print("|  " * indent + self.value)

    # ---------- variables ----------

    @addToClass(AST.Variable)
    def printTree(self, indent=0):
        print("|  " * indent+ self.name)

    # ---------- expressions ----------

    @addToClass(AST.BinExpr)
    def printTree(self, indent=0):
        print("|  " * indent + self.op)
        self.left.printTree(indent + 1)
        self.right.printTree(indent + 1)

    @addToClass(AST.UnExpr)
    def printTree(self, indent=0):
        print("|  " * indent + self.op)
        self.expr.printTree(indent + 1)

    @addToClass(AST.Transpose)
    def printTree(self, indent=0):
        print("|  " * indent + "TRANSPOSE")
        self.expr.printTree(indent + 1)

    @addToClass(AST.BuiltinCall)
    def printTree(self, indent=0):
        print("|  " * indent + self.name.upper())
        self.arg.printTree(indent + 1)

    @addToClass(AST.Vector)
    def printTree(self, indent=0):
        print("|  " * indent + "VECTOR")
        for elem in self.elements:
            elem.printTree(indent + 1)

    @addToClass(AST.Matrix)
    def printTree(self, indent=0):
        print("|  " * indent + "MATRIX")
        for row in self.rows:
            print("|  " * (indent + 1) + "VECTOR")
            for elem in row:
                elem.printTree(indent + 2)

    @addToClass(AST.Slice)
    def printTree(self, indent=0):
        print("|  " * indent + "SLICE")
        self.start.printTree(indent + 1)
        self.step.printTree(indent + 1)
        self.end.printTree(indent + 1)

    @addToClass(AST.Index)
    def printTree(self, indent=0):
        print("|  " * indent + "INDEX")
        self.collection.printTree(indent + 1)
        for idx in self.indices:
            idx.printTree(indent + 1)

    # ---------- statements / blocks / program ----------

    @addToClass(AST.Program)
    def printTree(self, indent=0):
        for stmt in self.statements:
            stmt.printTree(indent)

    @addToClass(AST.ExprStmt)
    def printTree(self, indent=0):
        self.expr.printTree(indent)

    @addToClass(AST.Assign)
    def printTree(self, indent=0):
        print("|  " * indent + "=")
        self.target.printTree(indent + 1)
        self.value.printTree(indent + 1)

    @addToClass(AST.AssignIndex)
    def printTree(self, indent=0):
        print("|  " * indent + "=")
        self.target.printTree(indent + 1)
        self.value.printTree(indent + 1)

    @addToClass(AST.Print)
    def printTree(self, indent=0):
        print("|  " * indent + "PRINT")
        for expression in self.expr_list:
            expression.printTree(indent + 1)

    @addToClass(AST.Break)
    def printTree(self, indent=0):
        print("|  " * indent + "BREAK")

    @addToClass(AST.Continue)
    def printTree(self, indent=0):
        print("|  " * indent + "CONTINUE")

    @addToClass(AST.Return)
    def printTree(self, indent=0):
        print("|  " * indent + "RETURN")
        if self.expr is not None:
            self.expr.printTree(indent + 1)

    @addToClass(AST.Block)
    def printTree(self, indent=0):
        if self.statements == []:
            print("|  " * indent + "EMPTY BLOCK")
        else:
            for stmt in self.statements:
                stmt.printTree(indent)

    @addToClass(AST.If)
    def printTree(self, indent=0):
        print("|  " * indent + "IF")
        self.condition.printTree(indent + 1)
        print("|  " * indent + "THEN")
        self.then_block.printTree(indent + 1)
        if self.else_block is not None:
            print("|  " * indent + "ELSE")
            self.else_block.printTree(indent + 1)

    @addToClass(AST.While)
    def printTree(self, indent=0):
        print("|  " * indent + "WHILE")
        self.condition.printTree(indent + 1)
        self.body.printTree(indent + 1)

    @addToClass(AST.For)
    def printTree(self, indent=0):
        print("|  " * indent + "FOR")
        self.var.printTree(indent + 1)
        print("|  " * (indent + 1) + "RANGE")
        self.start.printTree(indent + 2)
        self.end.printTree(indent + 2)
        self.body.printTree(indent + 1)

    # ---------- error ----------

    @addToClass(AST.Error)
    def printTree(self, indent=0):
        msg = self.message if self.message is not None else ""
        print("|  " * indent + "ERROR " + msg)
