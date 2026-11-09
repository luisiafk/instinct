import unittest
from src.instinct.backend.parser import Parser
from src.instinct.backend.lexer import Lexer  # O tu clase de lexer correspondiente
from src.instinct.backend.semantic import SemanticAnalyzer, SemanticError

class TestCreatureCompiler(unittest.TestCase):
    def run_compilation(self, code):
        # Asegúrate de ajustar esto según cómo invoques tu Lexer y Parser
        lexer = Lexer(code)
        tokens = lexer.tokenize() if hasattr(lexer, 'tokenize') else lexer
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast)
        return ast

    def test_valid_script(self):
        code = """
        creature TestBot
        faction Alpha
        health 100
        vision 5
        lifespan 50
        
        start:
        x = 10
        move(1, 0)
        if enemy_dist >= 0 goto start
        """
        try:
            self.run_compilation(code)
        except Exception as e:
            self.fail(f"Un script válido falló inesperadamente: {e}")

    def test_missing_start_label(self):
        code = """
        creature TestBot
        faction Alpha
        health 100
        vision 5
        lifespan 50

        # Falta la etiqueta start:
        x = 10
        """
        with self.assertRaises(SyntaxError):
            self.run_compilation(code)

    def test_invalid_header_values(self):
        code = """
        creature TestBot
        faction Alpha
        health 0
        vision 5
        lifespan 50

        start:
        x = 10
        """
        with self.assertRaises(SyntaxError):
            self.run_compilation(code)

    def test_readonly_assignment_error(self):
        code = """
        creature TestBot
        faction Alpha
        health 100
        vision 5
        lifespan 50

        start:
        health = 999
        """
        with self.assertRaises((SemanticError, SyntaxError)):
            self.run_compilation(code)

    def test_constant_assignment_error(self):
        code = """
        creature TestBot
        faction Alpha
        health 100
        vision 5
        lifespan 50

        start:
        GROUND = 5
        """
        with self.assertRaises((SemanticError, SyntaxError)):
            self.run_compilation(code)

    def test_function_arity_error(self):
        code = """
        creature TestBot
        faction Alpha
        health 100
        vision 5
        lifespan 50

        start:
        move(1)
        """
        with self.assertRaises((SemanticError, SyntaxError)):
            self.run_compilation(code)

    def test_syntax_garbage_rejection(self):
        code = """
        creature TestBot
        faction Alpha
        health 100
        vision 5
        lifespan 50

        start:
        42 + +
        """
        with self.assertRaises(SyntaxError):
            self.run_compilation(code)

if __name__ == '__main__':
    unittest.main()