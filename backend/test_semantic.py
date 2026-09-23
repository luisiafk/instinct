from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer, SemanticError

def run_test(title, code_str):
    print(f"\n----- Pruebas: {title} ----")
    try:
        lexer = Lexer(code_str)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)

    except SemanticError as e:
        print(f"Error Semantico Capturado: {e}")
    except Exception as e:
        print(f"Error inesperado {e}")

#test 1
valid_code = """
creature Uruk
faction Isengard
health 80
vision 6
lifespan 400

start:
if health < 20 goto flee
x = 5 + 3 * 2
goto start

flee:
say:("Huir!")
"""


invalid_label_code = """
creature Uruk
faction Isengard
health 80
vision 6
lifespan 400

start:
goto etiqueta_fantasma
"""

invalid_var_code = """
creature Uruk
faction Isengard
health 80
vision 6
lifespan 400

start:
x = variable_no_declarada + 10
"""

pdf_code = """
creature Uruk
faction Isengard
health 80
vision 6
lifespan 400

start:
    if health < 20 goto flee
    if enemy_dist == 1 goto bite
    if enemy_dist > 0 goto hunt
    if health > 70 and allies_near < 2 goto breed
    if allies_near > 3 goto celebrate

wander:
    move(random % 3 - 1, random % 3 - 1, 1)
    goto start

bite:
    consume(enemy_dx, enemy_dy, 15, 15)
    goto start

hunt:
    move(enemy_dx, enemy_dy, 2)
    goto start

flee:
    move(-enemy_dx, -enemy_dy, 3)
    goto start

breed:
    # bred in the pits of Isengard
    if see(x, y + 1) != GROUND goto wander
    reproduce(0, 1, 30)
    goto start

celebrate:
    say("Meat is back on the menu")
    roar("We are the fighting Uruk-hai")
    goto start
"""


run_test("Caso del pdf", pdf_code)

