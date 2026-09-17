import re
from enum import Enum
from dataclasses import dataclass
from typing import Any

class TokenType(Enum):
    #LITERALES
    NUMBER = (r'-?\d+', False)
    STRING = (r'"([^"\n]*)"', False)
    IDENTIFIER = (r'[a-zA-z_]\w*', False)

    #OPERADORES
    PLUS = (r'\+', False)
    MINUS = (r'-', False)
    MULTIPLY = (r'\*', False)
    DIVIDE = (r'/', False)
    MODULO = (r'%', False)
    ASSIGN = (r'=', False)

    #COMPARACION
    EQUAL = (r'==', False)
    NOT_EQUAL = (r'!=', False)
    GREATEREQUAL = (r'>=', False)
    LESSEQUAL = (r'<=', False)
    GREATER = (r'>', False)
    LESS = (r'<', False)

    #LOGICA
    AND = (r'\band\b', True)
    OR = (r'\bor\b', True)
    NOT = (r'\bnot\b', True)

    #DELIMITADORES
    LPAREN = (r'\(', False)
    RPAREN = (r'\)', False)
    COMMA = (r',', False)
    COLON = (r':', False)
    NEWLINE = (r'\n+', False)
    WHITESPACE = (r'[ \t]+', False)
    EOF = (r'$', False)
    MISMATCH = (r'.', False)

    def __init__(self, pattern: str, is_keyword: bool):
        self.pattern = pattern
        self.is_keyword = is_keyword
        self._compiled_regex = re.compile(f"^{pattern}")

    @classmethod
    def keywords(cls) -> dict[str, 'TokenType']:
        if not hasattr(cls, "_kw_map"):
            cls._kw_map = {member.name.lower(): member for member in cls if member.is_keyword}
        return cls._kw_map

    @classmethod
    def get_token_spec(cls) -> list[tuple[str, str]]:
        return [(token.name, token.pattern) for token in cls]

@dataclass
class Token:
    type: TokenType
    value: Any
    line: int
    column: int


    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r} at {self.line}:{self.column})"