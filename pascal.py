INTEGER, ADD, SUB, MUL, DIV, EOF, LPAR, RPAR = 'INTEGER', 'ADD', 'SUB', 'MUL', 'DIV', 'EOF', 'LPAR', 'RPAR'
BEGIN, END, DOT, ID, ASSIGN, SEMI = 'BEGIN', 'END', 'DOT', 'ID', 'ASSIGN', 'SEMI'


class Token:
    def __init__(self, type: str, val: object) -> None:
        self.type = type
        self.val = val
    
    def __str__(self) -> str:
        return f"Token({self.type}, {self.val})"


RESERVED_KEYWORDS = {
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END')
}


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.curr_char = self.text[self.pos]
    
    def error(self):
        raise Exception("Invalid char")

    def _id(self):
        res = ''
        while self.curr_char is not None and self.curr_char.isalnum():
            res += self.curr_char
            self.advance()
        
        token = RESERVED_KEYWORDS.get(res, Token(ID, res))
        return token

    def peek(self) -> str:
        peek_pos = self.pos + 1
        if peek_pos >= len(self.text):
            return None
        return self.text[peek_pos]
    
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
        if self.curr_char.isalpha():
            return self._id()
        if self.curr_char == '.':
            self.advance()
            return Token(DOT, '.')
        if self.curr_char == ';':
            self.advance()
            return Token(SEMI, ';')
        if self.curr_char == ':' and self.peek() == '=':
            self.advance()
            self.advance()
            return Token(ASSIGN, ':=')
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


class Compound(AST):
    def __init__(self) -> None:
        self.children = []


class Assign(AST):
    def __init__(self, left: Token, op: Token, right: Token) -> None:
        self.left = left
        self.node = self.op = op
        self.right = right


class Var(AST):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.val = token.val


class NoOp(AST):
    pass


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.curr_token = self.lexer.get_next_token()
    
    def error(self):
        raise Exception("Invalid syntax")
    
    def parse(self):
        node = self.program()
        if self.curr_token.type != EOF:
            self.error()
        return node
    
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
        else:
            node = self.variable()
            return node

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
    
    def program(self) -> Compound:
        node = self.compound_statement()
        self.eat(DOT)
        return node
    
    def compound_statement(self) -> Compound:
        self.eat(BEGIN)
        nodes = self.statement_list()
        self.eat(END)

        root = Compound()
        for node in nodes:
            root.children.append(node)
        return root

    def statement_list(self) -> list[Compound | Assign | NoOp]:
        node = self.statement()
        res = [node]

        while self.curr_token.type == SEMI:
            self.eat(SEMI)
            res.append(self.statement())
        return res
    
    def statement(self) -> Compound | Assign | NoOp:
        if self.curr_token.type == BEGIN:
            node = self.compound_statement()
        elif self.curr_token.type == ID:
            node = self.assignment_statement()
        else:
            node = self.empty()
        return node
    
    def assignment_statement(self) -> Assign:
        left = self.variable()
        token = self.curr_token
        self.eat(ASSIGN)
        right = self.expr()
        node = Assign(left, token, right)
        return node
    
    def variable(self) -> Var:
        node = Var(self.curr_token)
        self.eat(ID)
        return node
    
    def empty(self) -> NoOp:
        return NoOp()
    

class NodeVisitor:
    def visit(self, node: AST) -> object:
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name)
        return visitor(node)


class Interpreter(NodeVisitor):
    def __init__(self, parser: Parser) -> None:
        self.parser = parser
        self.GLOBAL_SCOPE = {}

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
    
    def visit_Compound(self, node: Compound) -> None:
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node: Assign) -> None:
        var_name = node.left.val
        self.GLOBAL_SCOPE[var_name] = self.visit(node.right)

    def visit_Var(self, node: Var) -> int:
        var_name = node.val
        val = self.GLOBAL_SCOPE.get(var_name)

        if val is None:
            raise NameError(repr(var_name))
        else:
            return val

    def visit_NoOp(self, node: NoOp) -> None:
        pass

    def interpret(self) -> int:
        tree = self.parser.parse()
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
        print(interpreter.GLOBAL_SCOPE)

if __name__ == '__main__':
    main()
