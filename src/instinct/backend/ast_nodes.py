from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ASTNode:
    lineno : int

@dataclass
class HeaderNode(ASTNode):
    creature : str
    faction : str
    health : int
    vision : int
    lifespan : int


@dataclass
class ProgramNode(ASTNode):
    header : HeaderNode
    statements : List[ASTNode]

@dataclass
class LabelNode(ASTNode):
    name : str

@dataclass
class GotoNode(ASTNode):
    target : str

@dataclass
class IfGotoNode(ASTNode):
    condition : ASTNode
    target : str

@dataclass
class AssignNode(ASTNode):
    name : str
    value : ASTNode

@dataclass
class ActionNode(ASTNode):
    name : str
    args : List[ASTNode]


#EXPRESION NODES

@dataclass
class NumberNode(ASTNode):
    value : int

    def evaluate(self, memory):
        return self.value

@dataclass
class StringNode(ASTNode):
    value : str

    def evaluate(self, memory):
        return self.value

@dataclass
class IdentifierNode(ASTNode):
    name : str

    def evaluate(self, memory):
        if isinstance(memory, dict):
            return memory.get(self.name, 0)
        return getattr(memory, self.name, 0)

@dataclass
class FunctionCallNode(ASTNode):
    name : str
    args : List[ASTNode]

    def evaluate(self, memory: any) -> any:
        evaluated_args = [arg.evaluate(memory) for arg in self.args]

        if hasattr(memory, 'call_function'):
            return memory.call_function(self.name, evaluated_args)

        raise RuntimeError(f"Error en la linea {self.lineno}: Funcion o llamada desconocida '{self.name}'.")

@dataclass
class BinaryOpNode(ASTNode):
    left : ASTNode
    op : str
    right : ASTNode

    def evaluate(self, memory):
        left_val = self.left.evaluate(memory)
        right_val = self.right.evaluate(memory)

        if self.op == '+':
            return left_val + right_val
        elif self.op == '-':
            return left_val - right_val
        elif self.op == '*':
            return left_val * right_val
        elif self.op == '/':
            if right_val == 0:
                raise RuntimeError("Error en tiempo de ejecucion: Division por cero")
            return left_val // right_val
        elif self.op == '%':
            if right_val == 0:
                raise RuntimeError("Error en tiempo de ejecucion: Modulo por cero")
            return left_val % right_val
        elif self.op == '<':
            return 1 if left_val < right_val else 0
        elif self.op == '>':
            return 1 if left_val > right_val else 0
        elif self.op == '<=':
            return 1 if left_val <= right_val else 0
        elif self.op == '>=':
            return 1 if left_val >= right_val else 0
        elif self.op == '==':
            return 1 if left_val == right_val else 0
        elif self.op == '!=':
            return 1 if left_val != right_val else 0
        elif self.op == 'and':
            if not left_val:
                return False
            return bool(self.right.evaluate(memory))
        elif self.op == 'or':
            if not left_val:
                return True
            return bool(self.right.evaluate(memory))

        else:
            raise RuntimeError(f"Operador binario desconocido: {self.op}")

@dataclass
class UnaryOpNode(ASTNode):
    op : str
    operand : ASTNode

    def evaluate(self, memory):
        val = self.operand.evaluate(memory)

        if self.op == '-':
            return -val
        elif self.op in ('not', '!'):
            return 0 if val else 1
        else:
            raise RuntimeError(f"Operador unario desconocido {self.op}")


def dump_ast(node, indent=0):
    pad = " " * indent
    if hasattr(node, "__dataclass_fields__"):
        print(f"{pad}{node.__class__.__name__}:")
        for field in node.__dataclass_fields__:
            value = getattr(node, field)
            if isinstance(value, list):
                print(f"{pad} {field}: [")
                for item in value:
                    dump_ast(item, indent + 2)
                print(f"{pad} ]")
            elif hasattr(value, "__dataclass_fields__"):
                print(f"{pad} {field}:")
                dump_ast(value, indent + 2)
            else:
                print(f"{pad} {field}: {value}")
    else:
        print(f"{pad}{node}")
