from .ast_nodes import (
    ActionNode,
    AssignNode,
    BinaryOpNode,
    FunctionCallNode,
    GotoNode,
    IdentifierNode,
    IfGotoNode,
    LabelNode,
    NumberNode,
    ProgramNode,
    StringNode,
    UnaryOpNode,
)


class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        # Constantes, atributos y percepciones que no pueden modificarse.
        self.read_only = {
            # Constantes
            'GROUND', 'OBJECT', 'ALLY', 'ENEMY', 'NONE',

            # Datos de la criatura
            'creature', 'faction', 'species',
            'health', 'vision', 'lifespan', 'age',
            'orientation', 'x', 'y',

            # Percepciones de criaturas y objetos
            'allies_near', 'enemies_near', 'objects_near', 'consumables_near',


            'enemy_dist', 'enemy_dx', 'enemy_dy',
            'ally_dist', 'ally_dx', 'ally_dy',
            'object_dist', 'object_dx', 'object_dy',
            'consumable_dist', 'consumable_dx', 'consumable_dy',

            # Rugidos
            'roars_near', 'last_roar',

            # Entorno
            'terrain_here', 'reserve_here',
            'width', 'height', 'tick',

            # Estadísticas y valores especiales
            'total_creatures', 'total_allies',
            'total_enemies', 'random'
        }

        # Instrucciones que ejecutan acciones.
        self.valid_actions = {
            'move': 3,
            'attack': 3,
            'consume': 4,
            'reproduce': 3,
            'roar': 1,
            'say': 1,
            'wait': 1
        }

        # Funciones que devuelven valores.
        self.valid_functions = {
            'see': 2,
            'name': 2
        }

        self.declared_labels = set()

    def analyze(self, program: ProgramNode):
        self.declared_labels.clear()

        # Primera pasada: registrar etiquetas.
        for stmt in program.statements:
            if isinstance(stmt, LabelNode):
                if stmt.name in self.declared_labels:
                    raise SemanticError(
                        f"Error semántico en la línea {stmt.lineno}: "
                        f"etiqueta duplicada '{stmt.name}'."
                    )

                self.declared_labels.add(stmt.name)

        # Segunda pasada: analizar instrucciones.
        for stmt in program.statements:
            self.visit_statement(stmt)

    def visit_statement(self, stmt):
        if isinstance(stmt, LabelNode):
            pass

        elif isinstance(stmt, AssignNode):
            if stmt.name in self.read_only:
                raise SemanticError(
                    f"Error semántico en la línea {stmt.lineno}: "
                    f"no se puede asignar un valor a "
                    f"'{stmt.name}' porque es de solo lectura."
                )

            self.visit_expr(stmt.value)

        elif isinstance(stmt, GotoNode):
            if stmt.target not in self.declared_labels:
                raise SemanticError(
                    f"Error semántico en la línea {stmt.lineno}: "
                    f"la etiqueta '{stmt.target}' no está declarada."
                )

        elif isinstance(stmt, IfGotoNode):
            self.visit_expr(stmt.condition)

            if stmt.target not in self.declared_labels:
                raise SemanticError(
                    f"Error semántico en la línea {stmt.lineno}: "
                    f"la etiqueta '{stmt.target}' no está declarada."
                )

        elif isinstance(stmt, ActionNode):
            if stmt.name not in self.valid_actions:
                raise SemanticError(
                    f"Error semántico en la línea {stmt.lineno}: "
                    f"acción desconocida '{stmt.name}'."
                )

            expected_args = self.valid_actions[stmt.name]

            if len(stmt.args) != expected_args:
                raise SemanticError(
                    f"Error semántico en la línea {stmt.lineno}: "
                    f"cantidad incorrecta de argumentos para la acción "
                    f"'{stmt.name}': se esperaban {expected_args} y se "
                    f"recibieron {len(stmt.args)}."
                )

            for arg in stmt.args:
                self.visit_expr(arg)

        else:
            raise SemanticError(
                f"Error semántico: instrucción no reconocida "
                f"'{type(stmt).__name__}'."
            )

    def visit_expr(self, expr):
        if isinstance(expr, (NumberNode, StringNode, IdentifierNode)):
            return

        elif isinstance(expr, BinaryOpNode):
            self.visit_expr(expr.left)
            self.visit_expr(expr.right)

        elif isinstance(expr, UnaryOpNode):
            self.visit_expr(expr.operand)

        elif isinstance(expr, FunctionCallNode):
            if expr.name not in self.valid_functions:
                raise SemanticError(
                    f"Error semántico en la línea {expr.lineno}: "
                    f"función desconocida '{expr.name}'."
                )

            expected_args = self.valid_functions[expr.name]

            if len(expr.args) != expected_args:
                raise SemanticError(
                    f"Error semántico en la línea {expr.lineno}: "
                    f"cantidad incorrecta de argumentos para la función "
                    f"'{expr.name}': se esperaban {expected_args} y se "
                    f"recibieron {len(expr.args)}."
                )

            for arg in expr.args:
                self.visit_expr(arg)

        else:
            raise SemanticError(
                f"Error semántico: expresión no reconocida "
                f"'{type(expr).__name__}'."
            )