from .ast_nodes import (
    ProgramNode, LabelNode, AssignNode,
    IfGotoNode, GotoNode, ActionNode, BinaryOpNode,
    UnaryOpNode, NumberNode, StringNode, IdentifierNode,
    FunctionCallNode
)

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.read_only = {
            'GROUND', 'OBJECT', 'ALLY', 'ENEMY', 'NONE',
            'health', 'vision', 'lifespan', 'age', 'orientation',
            'allies_near', 'enemies_near', 'object_near',
            'ally_dist', 'ally_dx', 'ally_dy',
            'object_dist', 'object_dx', 'object_dy',
            'enemy_dist', 'enemy_dx', 'enemy_dy'
            'roars_near', 'last_roar'
        }
        self.valid_functions = {
            'move' : 2,
            'attack' : 2,
            'wait' : 1,
            'roar' : 1,
            'see' : 2,
            'name' : 0
        }
        self.declared_vars = set()
        self.declared_labels = set()

    def analyze(self, program : ProgramNode):
        self.declared_vars.clear()
        self.declared_labels.clear()


        if program.header:
            self.declared_vars.update({'creature', 'faction', 'health', 'vision', 'lifespan'})

        self.declared_vars.update(self.read_only)
        for stmt in program.statements:
            if isinstance(stmt, LabelNode):
                if stmt.name in self.declared_labels:
                    raise SemanticError(f"Duplicated Label '{stmt.name}'.")
                self.declared_labels.add(stmt.name)

        for stmt in program.statements:
            self.visit_statement(stmt)


    def visit_statement(self, stmt):
        if isinstance(stmt, LabelNode):
            pass
        elif isinstance(stmt, AssignNode):
            if stmt.name in self.read_only:
                raise SemanticError(f"Error en la linea {stmt.lineno}: No se puede asignar un valor a la constante o percepcion de solo lectura '{stmt.name}'.")

            self.visit_expr(stmt.value)
            self.declared_vars.add(stmt.name)

        elif isinstance(stmt, GotoNode):
            if stmt.target not in self.declared_labels:
                raise SemanticError(f"Error en la linea {stmt.lineno}: La etiqueta de destino '{stmt.target}' no esta declarada.")

        elif isinstance(stmt, IfGotoNode):
            self.visit_expr(stmt.condition)
            if stmt.target not in self.declared_labels:
                raise SemanticError(f"Error en la linea {stmt.lineno}: La etiqueta de destino '{stmt.target}' no esta declarada.")

        elif isinstance(stmt, ActionNode):
            if stmt.name not in self.valid_functions:
                raise SemanticError(f"Error en la linea {stmt.lineno}: Funcion desconocida '{stmt.name}'.")

            expected_args = self.valid_functions[stmt.name]
            if len(stmt.args) != expected_args:
                raise SemanticError(f"Error en la linea {stmt.lineno}: La funcion '{stmt.name}' espera {expected_args} argumentos pero recibio {len(stmt.args)}.")

            for arg in stmt.args:
                self.visit_expr(arg)

        else:
            raise SemanticError(f"Instruccion no reconocida: {type(stmt).__name__}.")

    def visit_expr(self, expr):
        if isinstance(expr, (NumberNode, StringNode)):
            return

        elif isinstance(expr, IdentifierNode):
            if expr.name not in self.declared_vars:
                raise SemanticError(f"Error en la linea {expr.lineno}: Variable no definida'{expr.name}'.")

        elif isinstance(expr, BinaryOpNode):
            self.visit_expr(expr.left)
            self.visit_expr(expr.right)

        elif isinstance(expr, UnaryOpNode):
            self.visit_expr(expr.operand)

        elif isinstance(expr, FunctionCallNode):
            if expr.name not in self.valid_functions:
                raise SemanticError(f"Error en la linea {expr.lineno}: Funcion desconocida '{expr.name}'.")

            expected_args = self.valid_functions[expr.name]
            if len(expr.args) != expected_args:
                raise SemanticError(f"Error en la linea {expr.lineno}: La funcion '{expr.name}' espera {expected_args} argumentos pero recibio {len(expr.args)}.")

            for arg in expr.args:
                self.visit_expr(arg)

        else:
            raise SemanticError(f"Expresion no reconocida: {type(expr).__name__}")



