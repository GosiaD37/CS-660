"""
Simple Arithmetic Interpreter
Grammar rules for arithmetic expressions with +, -, *, and parentheses:

expression -> term expression_tail
expression_tail -> + term expression_tail | - term expression_tail | epsilon
term -> factor term_tail
term_tail -> * factor term_tail | epsilon
factor -> number | ( expression )
number -> nonzero_digit digits
digits -> digit digits | epsilon
nonzero_digit -> 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
digit -> 0 | nonzero_digit

Operators at the same precedence level are evaluated left to right.
"""

class ASTNode:
    pass


class NumberNode(ASTNode):
    def __init__(self, value):
        self.value = value


class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right


class Parser:
    def __init__(self, expression):
        self.expr = expression.replace(' ', '')
        self.pos = 0
        self.current_char = self.expr[0] if self.expr else None

    def advance(self):
        self.pos += 1
        self.current_char = self.expr[self.pos] if self.pos < len(self.expr) else None

    def parse_number(self):
        # Parse integer and return NumberNode
        number = ''
        while self.current_char is not None and self.current_char.isdigit():
            number += self.current_char
            self.advance()
        return NumberNode(int(number))

    def parse_factor(self):
        # Implement factor parsing
        if self.current_char == '(':
            self.advance()
            node = self.parse_expression()
            self.advance()
            return node
        return self.parse_number()

    def parse_term(self):
        # Implement term parsing
        node = self.parse_factor()
        while self.current_char == '*':
            op = self.current_char
            self.advance()
            node = BinaryOpNode(node, op, self.parse_factor())
        return node

    def parse_expression(self):
        # Implement expression parsing
        node = self.parse_term()
        while self.current_char in ('+', '-'):
            op = self.current_char
            self.advance()
            node = BinaryOpNode(node, op, self.parse_term())
        return node


def evaluate(node):
    # Evaluate AST node recursively
    if isinstance(node, NumberNode):
        return node.value
    left = evaluate(node.left)
    right = evaluate(node.right)
    if node.op == '+':
        return left + right
    elif node.op == '-':
        return left - right
    elif node.op == '*':
        return left * right


def interpret(expression):
    parser = Parser(expression)
    ast = parser.parse_expression()
    return evaluate(ast)


# Test cases
if __name__ == "__main__":
    test_expressions = [
        "42",
        "2 + 3",
        "10 - 4",
        "3 * 7",
        "2 + 3 * 4",
        "(2 + 3) * 4",
        "1 + 2 + 3",
        "10 - 5 - 2",
        "((1 + 2) * 3) - 4"
    ]

    print("Malgorzata Debska")
    print("Arithmetic Interpreter Test")
    for expr in test_expressions:
        try:
            result = interpret(expr)
            print(f"{expr} = {result}")
        except Exception as e:
            print(f"Error interpreting '{expr}': {e}")
