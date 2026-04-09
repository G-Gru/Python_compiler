class Symbol:
    def __init__(self, name, type_):
        self.name = name
        self.type = type_


class VariableSymbol(Symbol):
    def __init__(self, name, type_):
        super().__init__(name, type_)


class SymbolTable(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.symbols = {}

    def put(self, name, symbol):
        self.symbols[name] = symbol

    def get(self, name):
        t = self
        while t is not None:
            if name in t.symbols:
                return t.symbols[name]
            t = t.parent
        return None

    def getParentScope(self):
        return self.parent

    def pushScope(self, name):
        return SymbolTable(self, name)

    def popScope(self):
        return self.parent
