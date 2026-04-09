from sly import Parser
from scanner import Scanner
from AST import *


class Mparser(Parser):

    tokens = Scanner.tokens
    debugfile = 'parser2.out'

    precedence = (
        ('nonassoc', 'IFX'),
        ('left', 'EQ', 'NE', 'LE', 'GE', '<', '>'),
        ('left', 'DOTPLUS', 'DOTMINUS', '+', '-'),
        ('left', 'DOTTIMES', 'DOTDIVIDE', '*', '/'),
        ('right', 'UPLUS', 'UMINUS'),
        ('right', 'TRANSPOSE'),
        ('nonassoc', 'POSTFIXATOM'),
    )

    # ---------- program / statement list ----------

    @_('stmts')
    def program(self, p):
        return Program(p.lineno, p.stmts)

    @_('stmt')
    def stmts(self, p):
        return [p.stmt]

    @_('stmts stmt')
    def stmts(self, p):
        return p.stmts + [p.stmt]

    # ---------- statements ----------

    @_('lvalue PLUSEQ expr ";"')
    def stmt(self, p):
        return AssignIndex(
            p.lineno,
            p.lvalue,
            BinExpr(p.lineno, '+', p.lvalue, p.expr)
        )

    @_('lvalue MINUSEQ expr ";"')
    def stmt(self, p):
        return AssignIndex(
            p.lineno,
            p.lvalue,
            BinExpr(p.lineno, '-', p.lvalue, p.expr)
        )

    @_('lvalue TIMESEQ expr ";"')
    def stmt(self, p):
        return AssignIndex(
            p.lineno,
            p.lvalue,
            BinExpr(p.lineno, '*', p.lvalue, p.expr)
        )

    @_('lvalue DIVEQ expr ";"')
    def stmt(self, p):
        return AssignIndex(
            p.lineno,
            p.lvalue,
            BinExpr(p.lineno, '/', p.lvalue, p.expr)
        )

    @_('lvalue ASSIGN expr ";"')
    def stmt(self, p):
        return AssignIndex(p.lineno, p.lvalue, p.expr)

    @_('PRINT expr_list ";"')
    def stmt(self, p):
        return Print(p.lineno, p.expr_list)

    @_('BREAK ";"')
    def stmt(self, p):
        return Break(p.lineno)

    @_('CONTINUE ";"')
    def stmt(self, p):
        return Continue(p.lineno)

    @_('RETURN ";"')
    def stmt(self, p):
        return Return(p.lineno, None)

    @_('RETURN expr ";"')
    def stmt(self, p):
        return Return(p.lineno, p.expr)

    @_('"{" stmts "}"')
    def block(self, p):
        return Block(p.lineno, p.stmts)

    @_('stmt')
    def statement_or_block(self, p):
        return Block(p.lineno, [p.stmt])

    @_('block')
    def statement_or_block(self, p):
        return p.block

    @_('IF "(" expr ")" statement_or_block %prec IFX')
    def stmt(self, p):
        return If(p.lineno, p.expr, p.statement_or_block, None)

    @_('IF "(" expr ")" statement_or_block ELSE statement_or_block')
    def stmt(self, p):
        return If(p.lineno, p.expr, p.statement_or_block0, p.statement_or_block1)

    @_('WHILE "(" expr ")" statement_or_block')
    def stmt(self, p):
        return While(p.lineno, p.expr, p.statement_or_block)

    @_('FOR ID ASSIGN expr ":" expr statement_or_block')
    def stmt(self, p):
        return For(p.lineno, Variable(p.lineno, p.ID), p.expr0, p.expr1, p.statement_or_block)

    # ---------- expressions ----------

    @_('expr "+" expr')
    def expr(self, p):
        return BinExpr(p.lineno, '+', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return BinExpr(p.lineno, '-', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return BinExpr(p.lineno, '*', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return BinExpr(p.lineno, '/', p.expr0, p.expr1)

    @_('expr DOTPLUS expr')
    def expr(self, p):
        return BinExpr(p.lineno, '.+', p.expr0, p.expr1)

    @_('expr DOTMINUS expr')
    def expr(self, p):
        return BinExpr(p.lineno, '.-', p.expr0, p.expr1)

    @_('expr DOTTIMES expr')
    def expr(self, p):
        return BinExpr(p.lineno, '.*', p.expr0, p.expr1)

    @_('expr DOTDIVIDE expr')
    def expr(self, p):
        return BinExpr(p.lineno, './', p.expr0, p.expr1)

    @_('expr EQ expr')
    def expr(self, p):
        return BinExpr(p.lineno, '==', p.expr0, p.expr1)

    @_('expr NE expr')
    def expr(self, p):
        return BinExpr(p.lineno, '!=', p.expr0, p.expr1)

    @_('expr LE expr')
    def expr(self, p):
        return BinExpr(p.lineno, '<=', p.expr0, p.expr1)

    @_('expr GE expr')
    def expr(self, p):
        return BinExpr(p.lineno, '>=', p.expr0, p.expr1)

    @_('expr "<" expr')
    def expr(self, p):
        return BinExpr(p.lineno, '<', p.expr0, p.expr1)

    @_('expr ">" expr')
    def expr(self, p):
        return BinExpr(p.lineno, '>', p.expr0, p.expr1)

    @_('"+" expr %prec UPLUS')
    def expr(self, p):
        return UnExpr(p.lineno, '+', p.expr)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return UnExpr(p.lineno, '-', p.expr)

    @_('transposed %prec POSTFIXATOM')
    def expr(self, p):
        return p.transposed

    @_('EYE "(" expr ")"')
    def expr(self, p):
        return BuiltinCall(p.lineno, "EYE", p.expr)

    @_('ZEROS "(" expr ")"')
    def expr(self, p):
        return BuiltinCall(p.lineno, "ZEROS", p.expr)

    @_('ONES "(" expr ")"')
    def expr(self, p):
        return BuiltinCall(p.lineno, "ONES", p.expr)

    # ---------- transposed----------

    @_('primary')
    def transposed(self, p):
        return p.primary

    @_('primary TRANSPOSE')
    def transposed(self, p):
        return Transpose(p.lineno, p.primary)

    # ---------- lvalue----------

    @_('ID')
    def lvalue(self, p):
        return Variable(p.lineno, p.ID)

    @_('ID "[" expr_list "]"')
    def lvalue(self, p):
        return Index(p.lineno, Variable(p.lineno, p.ID), p.expr_list)

    # ---------- primary ----------

    @_('"(" expr ")"')
    def primary(self, p):
        return p.expr

    @_('ID')
    def primary(self, p):
        return Variable(p.lineno, p.ID)

    @_('INTEGER')
    def primary(self, p):
        return IntNum(p.lineno, p.INTEGER)

    @_('FLOAT')
    def primary(self, p):
        return FloatNum(p.lineno, p.FLOAT)

    @_('STRING')
    def primary(self, p):
        return String(p.lineno, p.STRING)

    @_('matrix')
    def primary(self, p):
        return p.matrix

    @_('vector')
    def primary(self, p):
        return p.vector

    @_('primary "[" expr_list "]"')
    def primary(self, p):
        return Index(p.lineno, p.primary, p.expr_list)

    @_('primary "[" slice "]"')
    def primary(self, p):
        return Index(p.lineno, p.primary, p.slice)

    # ---------- slices ----------

    @_('expr ":" expr')
    def slice(self, p):
        return Slice(p.lineno, p.expr0, IntNum(p.lineno, 1), p.expr1)

    @_('expr ":" expr ":" expr')
    def slice(self, p):
        return Slice(p.lineno, p.expr0, p.expr1, p.expr2)

    @_('expr ":" ":" expr')
    def slice(self, p):
        return Slice(p.lineno, p.expr0, IntNum(p.lineno, 1), p.expr1)

    # ---------- vectors ----------

    @_('"[" expr_list "]"')
    def vector(self, p):
        return Vector(p.lineno, p.expr_list)

    # ---------- matrices ----------

    @_('"[" vector "," matrix_rows_tail "]"')
    def matrix(self, p):
        return Matrix(p.lineno, [p.vector.elements] + p.matrix_rows_tail)

    @_('matrix_rows_tail "," vector')
    def matrix_rows_tail(self, p):
        return p.matrix_rows_tail + [p.vector.elements]

    @_('vector')
    def matrix_rows_tail(self, p):
        return [p.vector.elements]

    @_('expr_list "," expr')
    def expr_list(self, p):
        return p.expr_list + [p.expr]

    @_('expr')
    def expr_list(self, p):
        return [p.expr]

    # ---------- error ----------

    def error(self, p):
        if p:
            print(f"sly: Syntax error at line {p.lineno}, token={p.type}")
        else:
            print("sly: Syntax error at EOF")
