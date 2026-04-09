class Memory:
    def __init__(self, name):
        self.name = name
        self._data = {}

    def has_key(self, name):
        return name in self._data

    def get(self, name):
        return self._data[name]

    def put(self, name, value):
        self._data[name] = value


class MemoryStack:
    def __init__(self, memory=None):
        self.stack = [memory if memory is not None else Memory("global")]

    def get(self, name):
        for mem in reversed(self.stack):
            if mem.has_key(name):
                return mem.get(name)
        raise KeyError(name)

    def insert(self, name, value):
        self.stack[-1].put(name, value)

    def set(self, name, value):
        for mem in reversed(self.stack):
            if mem.has_key(name):
                mem.put(name, value)
                return
        self.stack[-1].put(name, value)

    def push(self, memory):
        self.stack.append(memory)

    def pop(self):
        if len(self.stack) <= 1:
            raise RuntimeError("cannot pop global memory")
        return self.stack.pop()
