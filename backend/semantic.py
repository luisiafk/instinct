from re import I

from ast_nodes import (
    ProgramNode, LabelNode, AssignNode,
    IfGotoNode, GotoNode, ActionNode, BinaryOpNode,
    UnaryOpNode, NumberNode, StringNode, IdentifierNode
)

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    def __init__(self):
        self.declared_vars = set()
        self.declared_labels = set()

    def analyze(self, program : ProgramNode):
        self.declared_vars.clear()
        self.declared_labels.clear()


        if program.header:
            self.declared_vars.update({'creature', 'faction', 'health', 'vision', 'lifespan'})

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
            self.visit_expr(stmt.value)
            self.declared_vars.add(stmt.name)

        elif isinstance(stmt, GotoNode):
            if stmt.target not in self.declared_labels:
                raise SemanticError(f"Error on 'goto': destiny label '{stmt.target}' is not declared.")

        elif isinstance(stmt, IfGotoNode):
            self.visit_expr(stmt.condition)
            if stmt.target not in self.declared_labels:
                raise SemanticError(f"Error on 'if .. goto': destiny label '{stmt.target}' is not declared.")

        elif isinstance(stmt, ActionNode):
            for arg in stmt.args:
                self.visit_expr(arg)

        else:
            raise SemanticError(f"Instruction no recognized: {type(stmt).__name__}.")

    def visit_expr(self, expr):
        if isinstance(expr, (NumberNode, StringNode)):
            return

        elif isinstance(expr, IdentifierNode):
            if expr.name not in self.declared_vars:
                raise SemanticError(f"Variable mot defined '{expr.name}'.")

        elif isinstance(expr, BinaryOpNode):
            self.visit_expr(expr.left)
            self.visit_expr(expr.right)

        else:
            raise SemanticError(f"Expression not recognized: {type(expr).__name__}")



