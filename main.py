import sys
from scanner import Scanner
from parser import Mparser
import TreePrinter
from TypeChecker import TypeChecker
from Interpreter import Interpreter


if __name__ == "__main__":
    try:
        filename = sys.argv[1] if len(sys.argv) > 1 else "../examples/fibonacci.m"
        with open(filename, "r") as file:
            text = file.read()
    except IOError:
        print(f"Cannot open {filename} file")
        sys.exit(0)

    lexer = Scanner()
    parser = Mparser()

    ast = parser.parse(lexer.tokenize(text))
    if ast is None:
        sys.exit(1)

    ast.printTree()

    typeChecker = TypeChecker()
    typeChecker.visit(ast)

    if getattr(typeChecker, "errors", []):
        sys.exit(1)

    try:
        Interpreter().visit(ast)
    except Exception as e:
        print(f"Runtime error: {e}")
        sys.exit(1)
