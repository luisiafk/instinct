from dataclasses import dataclass
from typing import List, Optional

class ASTNode:
    pass

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

@dataclass
class StringNode(ASTNode):
    value : str

@dataclass
class IdentifierNode(ASTNode):
    name : str

@dataclass
class FunctionCallNode(ASTNode):
    name : str
    args : List[ASTNode]


@dataclass
class BinaryOpNode(ASTNode):
    left : ASTNode
    op : str
    right : ASTNode

@dataclass
class UnaryOpNode(ASTNode):
    op : str
    operand : ASTNode


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
