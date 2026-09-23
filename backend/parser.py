from token import LESS

from tokens import TokenType
from ast_nodes import (
    ProgramNode, HeaderNode, LabelNode,
    GotoNode, IfGotoNode, AssignNode,
    ActionNode, NumberNode, StringNode,
    IdentifierNode, FunctionCallNode,
    BinaryOpNode, UnaryOpNode
)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current = self.tokens[self.pos] if self.tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]
        else:
            self.current = None
        return self.current

    def match(self, token_type):
        return self.current and self.current.type == token_type


    def consume(self, token_type, error_msg):
        if self.match(token_type):
            token = self.current
            self.advance()
            return token
        raise SyntaxError(f"Syntax Error line {getattr(self.current, 'line', '?')} : {error_msg}")

    def peek_type(self):
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1].type
        return None


    def parse(self):
        header = self.parse_header()
        statements = self.parse_body()
        return ProgramNode(header=header, statements=statements)


    def parse_header(self):
        header_data = {}
        required_keys = {'creature', 'faction', 'health', 'vision', 'lifespan'}

        while self.current and len(header_data) < 5:
            if self.match(TokenType.IDENTIFIER) and self.current.value == 'start':
                break

            if self.match(TokenType.IDENTIFIER):
                key = self.current.value
                self.advance()

                if key in  ('creature', 'faction'):
                    val_token = self.consume(TokenType.IDENTIFIER, f"Waiting a name for '{key}'")
                    header_data[key] = val_token.value
                elif key in ('health', 'vision', 'lifespan'):
                    val_token = self.consume(TokenType.NUMBER, f"Waitin a integer for '{key}")
                    header_data[key] = int(val_token.value)
                else:
                    raise SyntaxError(f"Header Keyword unkwon or out of site: '{key}'")
            else:
                self.advance()

        missing = required_keys - set(header_data.keys())
        if missing:
            raise SyntaxError(f"Missing atributes in the header: {', '.join(missing)}")

        return HeaderNode(
            creature=header_data['creature'],
            faction=header_data['faction'],
            health=header_data['health'],
            vision=header_data['vision'],
            lifespan=header_data['lifespan']
        )

    def parse_body(self):
        statements = []
        while self.current:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def parse_statement(self):
        if self.match(TokenType.IDENTIFIER) and self.peek_type() == TokenType.COLON:
            label_name = self.current.value
            self.advance()
            self.advance()
            return LabelNode(name=label_name)

        if self.match(TokenType.GOTO):
            self.advance()
            target_token = self.consume(TokenType.IDENTIFIER, "Wait for the label")
            return GotoNode(target=target_token.value)

        if self.match(TokenType.IF):
            self.advance()
            condition = self.parse_expr()
            self.consume(TokenType.GOTO, "Waiting for the 'goto' after the 'if' statment")
            target_token = self.consume(TokenType.IDENTIFIER, "Waiting for the label")
            return IfGotoNode(condition=condition, target=target_token.value)

        if self.match(TokenType.IDENTIFIER):
            ident_token = self.current
            self.advance()

            if self.match(TokenType.ASSIGN):
                self.advance()
                expr = self.parse_expr()
                return AssignNode(name=ident_token.value, value=expr)

            elif self.match(TokenType.LPAREN):
                self.advance()
                args = self.parse_arguments()
                self.consume(TokenType.RPAREN, "Parenthisis not closed missing ')'")
                return ActionNode(name=ident_token.value, args=args)

            else:
                raise SyntaxError(f"Instruction not valid for '{ident_token.value}'")

        self.advance()
        return None

    def parse_arguments(self):
        args = []
        if not self.match(TokenType.RPAREN):
            args.append(self.parse_expr())
            while self.match(TokenType.COMMA):
                self.advance()
                args.append(self.parse_expr())
        return args

    def parse_expr(self):
        left = self.parse_and()

        while self.match(TokenType.OR):
            op_token = self.current
            self.advance()
            right = self.parse_and()
            left = BinaryOpNode(left=left, op=op_token.value , right=right)

        return left

    def parse_and(self):
        left = self.parse_equality()

        while self.match(TokenType.AND):
            op_token = self.current
            self.advance()
            right = self.parse_equality()
            left = BinaryOpNode(left=left, op=op_token.value, right=right)

        return left

    def parse_equality(self):
        left = self.parse_additive()
        print("Token actual", self.current)
        print("Matchea con LESS", self.current.type == TokenType.LESS if self.current else False)


        while self.current and self.current.type in (
            TokenType.EQUAL, TokenType.NOT_EQUAL,
            TokenType.LESS, TokenType.LESSEQUAL,
            TokenType.GREATER, TokenType.GREATEREQUAL
        ):
            op_token = self.current
            self.advance()
            right = self.parse_additive()
            left = BinaryOpNode(left=left, op=op_token.value, right=right)

        return left

    def parse_additive(self):
        left = self.parse_multiplicative()

        while self.current and self.current.type in(TokenType.PLUS, TokenType.MINUS):
            op_token = self.current
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOpNode(left=left, op=op_token.value, right=right)

        return left

    def parse_multiplicative(self):
        left = self.parse_unary()

        while self.current and self.current.type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_token = self.current
            self.advance()
            right = self.parse_unary()
            left = BinaryOpNode(left=left, op=op_token.value, right=right)

        return left

    def parse_unary(self):
        if self.current and self.current.type in (TokenType.MINUS, TokenType.NOT):
            op_token = self.current
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode(op=op_token.value, operand=operand)

        return self.parse_primary()

    def parse_primary(self):
        if self.match(TokenType.NUMBER):
            val = self.current
            self.advance()
            return NumberNode(value=int(val.value))

        if self.match(TokenType.STRING):
            val = self.current
            self.advance()
            return StringNode(value=val.value)

        if self.match(TokenType.IDENTIFIER):
            ident_token = self.current
            self.advance()

            if self.match(TokenType.LPAREN):
                self.advance()
                args = self.parse_arguments()
                self.consume(TokenType.RPAREN, "Missin ')' after the args")
                return FunctionCallNode(name=ident_token.value, args=args)

            return IdentifierNode(name=ident_token.value)


        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expr()
            self.consume(TokenType.RPAREN, "Missin ')' after the args")
            return expr

        raise SyntaxError(f"Expression not valid, Unexpected Token: {self.current}")