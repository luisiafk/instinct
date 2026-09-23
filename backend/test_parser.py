from tokens import TokenType
from lexer import Lexer
from parser import Parser
from ast_nodes import dump_ast


test_code = """ creature Uruk faction Isengard health 80 vision 6 lifespan 400
start: if health < 20 goto flee x = 5 + 3 * 2 move(1, 0, 1) goto start
flee: say("huir!") """

lexer = Lexer(test_code)
tokens = lexer.tokenize()
print(tokens)

parser = Parser(tokens)
ast = parser.parse()
print("=== AST GENERADO CON ÉXITO ===")
dump_ast(ast)