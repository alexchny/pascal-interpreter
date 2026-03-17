INTEGER, ADD, SUB, MUL, DIV, EOF, LPAR, RPAR = 'INTEGER', 'ADD', 'SUB', 'MUL', 'DIV', 'EOF', 'LPAR', 'RPAR'


class Token:
    def __init__(self, type: str, val: int) -> None:
        self.type = type
        self.val = val
    
    def __str__(self) -> str:
        return f"Token({self.type}, {self.val})"


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.curr_char = self.text[self.pos]
    
    def error(self):
        raise Exception("Invalid char")
    
    def advance(self) -> None:
        self.pos += 1
        if self.pos >= len(self.text):
            self.curr_char = None
        else:
            self.curr_char = self.text[self.pos]

    def skip_whitespace(self) -> None:
         while self.curr_char is not None and self.curr_char.isspace():
            self.advance()
        
    def integer(self) -> int:
        res = ""
        while self.curr_char is not None and self.curr_char.isdigit():
            res += self.curr_char
            self.advance()
        return int(res)

    def get_next_token(self) -> Token:
        self.skip_whitespace()

        if self.pos >= len(self.text):
            return Token(EOF, None)
        if self.curr_char.isdigit():
            return Token(INTEGER, self.integer())
        if self.curr_char == '+':    
            self.advance()
            return Token(ADD, '+')
        if self.curr_char == '-':    
            self.advance()
            return Token(SUB, '-')
        if self.curr_char == '*':    
            self.advance()
            return Token(MUL, '*')
        if self.curr_char == '/':    
            self.advance()
            return Token(DIV, '/')
        if self.curr_char == '(':
            self.advance()
            return Token(LPAR, '(')
        if self.curr_char == ')':
            self.advance()
            return Token(RPAR, ')')

        self.error()


class AST:
    pass


class BinOp(AST):
    def __init__(self, left: Token, op: Token, right: Token) -> None:
        self.left = left
        self.token = self.op = op
        self.right = right


class UnaryOp(AST):
    def __init__(self, op: Token, expr: AST) -> None:
        self.token = self.op = op
        self.expr = expr


class Num(AST):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.val = token.val


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.curr_token = self.lexer.get_next_token()
    
    def error(self):
        raise Exception("Invalid syntax")
    
    def eat(self, type: str) -> None:
        if self.curr_token.type == type:
            self.curr_token = self.lexer.get_next_token()
        else:
            self.error()
    
    def factor(self) -> Num | BinOp | UnaryOp:
        token = self.curr_token

        if token.type == ADD:
            self.eat(ADD)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == SUB:
            self.eat(SUB)
            node = UnaryOp(token, self.factor())
            return node
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == LPAR:
            self.eat(LPAR)
            node = self.expr()
            self.eat(RPAR)
            return node
        
        self.error()

    def term(self) -> Num | BinOp:
        node = self.factor()

        while self.curr_token.type in (MUL, DIV):
            token = self.curr_token

            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
        
            node = BinOp(left=node, op=token, right=self.factor())
        
        return node

    def expr(self) -> Num | BinOp:
        node = self.term()

        while self.curr_token.type in (ADD, SUB):
            token = self.curr_token

            if token.type == ADD:
                self.eat(ADD)
            elif token.type == SUB:
                self.eat(SUB)

            node = BinOp(left=node, op=token, right=self.term())
        
        return node


class NodeVisitor:
    def visit(self, node: AST) -> object:
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name)
        return visitor(node)


class Interpreter(NodeVisitor):
    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def visit_BinOp(self, node: BinOp) -> int:
        if node.op.type == ADD:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == SUB:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) // self.visit(node.right)

    def visit_Num(self, node: Num) -> int:
        return node.val

    def visit_UnaryOp(self, node: UnaryOp) -> int:
        op = node.op.type
        if op == ADD:
            return +self.visit(node.expr)
        elif op == SUB:
            return -self.visit(node.expr)

    def interpret(self) -> int:
        tree = self.parser.expr()
        return self.visit(tree)


def main():
    while True:
        try:
            text = input('pascal> ')
        except EOFError:
            break
        if not text:
            continue
        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        res = interpreter.interpret()
        print(res)

if __name__ == '__main__':
    main()
