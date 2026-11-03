import os
from .lexer import Lexer
from .parser import Parser
from .semantic import SemanticAnalyzer

def compile_file(filepath: str):
    if not os.path.exists(filepath):
        print(f"[!] archivo de script no encontrado: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    lexer = Lexer(code)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)

    return ast