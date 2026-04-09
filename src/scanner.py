# new/scanner.py
import sys
from sly import Lexer


class Scanner(Lexer):
    lineno = 1
    reserved = {
        'break': 'BREAK',
        'continue': 'CONTINUE',
        'if': 'IF',
        'else': 'ELSE',
        'while': 'WHILE',
        'print': 'PRINT',
        'for': 'FOR',
        'return': 'RETURN',
        'eye': 'EYE',
        'zeros': 'ZEROS',
        'ones': 'ONES',
    }

    tokens = [
        'ID', 'STRING',
        'DOTPLUS', 'DOTMINUS', 'DOTTIMES', 'DOTDIVIDE',
        'ASSIGN', 'PLUSEQ', 'MINUSEQ', 'TIMESEQ', 'DIVEQ',
        'LE', 'GE', 'NE', 'EQ',
        'TRANSPOSE', 'FLOAT', 'INTEGER',
    ] + list(reserved.values())

    literals = {'+', '-', '*', '/', '<', '>', '(', ')', '[', ']', '{', '}', ':', ',', ';', "'", }

    ignore = ' \t'
    ignore_comment = r'\#.*'

    DOTPLUS     = r'\.\+'
    DOTMINUS    = r'\.-'
    DOTTIMES    = r'\.\*'
    DOTDIVIDE   = r'\./'
    PLUSEQ      = r'\+='
    MINUSEQ     = r'-='
    TIMESEQ     = r'\*='
    DIVEQ       = r'/='
    LE          = r'<='
    GE          = r'>='
    NE          = r'!='
    EQ          = r'=='
    TRANSPOSE   = r"'"
    ASSIGN      = r'='

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    def ID(self, t):
        t.lineno = self.lineno
        t.type = self.reserved.get(t.value, 'ID')
        return t

    FLOAT = r'((\d+\.\d*|\.\d+)([eE][-+]?\d+)?)|\d+[eE][-+]?\d+'
    def FLOAT(self, t):
        t.lineno = self.lineno
        t.value = float(t.value)
        return t

    INTEGER = r'\d+'
    def INTEGER(self, t):
        t.lineno = self.lineno
        t.value = int(t.value)
        return t

    STRING = r'"([^"\\]|\\.)*"'
    def STRING(self, t):
        t.lineno = self.lineno
        t.value = bytes(t.value[1:-1], "utf-8").decode("unicode_escape")
        return t

    ignore_newline = r'\n+'
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1


if __name__ == '__main__':

    lexer = Scanner()

    filename = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
    with open(filename, "r") as file:
        text = file.read()

    for tok in lexer.tokenize(text):
        print(f"{tok.lineno}: {tok.type}({tok.value})")
