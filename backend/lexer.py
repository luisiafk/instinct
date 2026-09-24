import re
from token import NEWLINE
from tokens import TokenType, Token

class LexerError(Exception):
    pass

class Lexer:
    def __init__(self, code: str):
        self.code = code
        regex_parts = [f"(?P<{token.name}>{token.pattern})" for token in TokenType]
        self.master_regex = re.compile("|".join(regex_parts))

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        line = 1
        line_start = 0

        for match in self.master_regex.finditer(self.code):
            kind = match.lastgroup
            value = match.group()
            column = match.start() - line_start + 1

            if kind == "WHITESPACE":
                continue

            if kind == "NEWLINE":
                tokens.append(Token(type=TokenType.NEWLINE, value="\n", line=line, column=column))
                line += value.count('\n')
                line_start = match.end()
                continue

            if kind == "COMMENT":
                continue


            if kind == "MISMATCH":
                raise LexerError(f"Caracter no permitido {value!r} en la line {line}, columna {column}")

            token_type = TokenType[str(kind)]
            parsed_value: str | int = value

            if token_type == TokenType.NUMBER:
                parsed_value = int(value)
            elif token_type == TokenType.STRING:
                parsed_value = value[1:-1]
            elif token_type == TokenType.IDENTIFIER:
                token_type = TokenType.keywords().get(value, TokenType.IDENTIFIER)

            tokens.append(Token(type=token_type, value=parsed_value, line=line, column=column))
        return tokens
