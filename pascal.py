ADD, SUB, MUL, DIV, FDIV, INTEGER, REAL, EOF, LPAR, RPAR, DOT, COLON, COMMA, ID, ASSIGN, SEMI = 'ADD', 'SUB', 'MUL', 'DIV', 'FDIV', 'INTEGER', 'REAL', 'EOF', 'LPAR', 'RPAR', 'DOT', 'COLON', 'COMMA', 'ID', 'ASSIGN', 'SEMI'
PROGRAM, VAR, BEGIN, END, INTEGER_TYPE, REAL_TYPE = 'PROGRAM', 'VAR', 'BEGIN', 'END', 'INTEGER_TYPE', 'REAL_TYPE'


class Token:
    def __init__(self, type: str, val: object) -> None:
        self.type = type
        self.val = val
    
    def __str__(self) -> str:
        return f"Token({self.type}, {self.val})"


RESERVED_KEYWORDS = {
    'PROGRAM': Token('PROGRAM', 'PROGRAM'),
    'VAR': Token('VAR', 'VAR'),
    'BEGIN': Token('BEGIN', 'BEGIN'),
    'END': Token('END', 'END'),
    'INTEGER': Token(INTEGER_TYPE, 'INTEGER'),
    'REAL': Token(REAL_TYPE, 'REAL'),
    'DIV': Token('DIV', 'DIV')
}


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.curr_char = self.text[self.pos] if self.text else ''
    
    def error(self):
        raise Exception("Invalid char")

    def _id(self):
        res = ''
        while self.curr_char is not None and (self.curr_char.isalnum() or self.curr_char == '_'):
            res += self.curr_char
            self.advance()
        
        res = res.upper()
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
    
    def skip_comment(self) -> None:
        while self.curr_char != '}':
            self.advance()
        self.advance()
        
    def number(self) -> Token:
        res = ""
        while self.curr_char is not None and (self.curr_char.isdigit() or (self.curr_char == '.' and '.' not in res)):
            res += self.curr_char
            self.advance()
        
        if '.' not in res:
            token = Token(INTEGER, int(res))
        else:
            token = Token(REAL, float(res))
        return token

    def get_next_token(self) -> Token:
        while self.curr_char is not None:
            self.skip_whitespace()

            if self.pos >= len(self.text):
                return Token(EOF, None)
            if self.curr_char.isdigit():
                return self.number()
            if self.curr_char.isalpha() or self.curr_char == '_':
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
            if self.curr_char == ':':
                self.advance()
                return Token(COLON, ':')
            if self.curr_char == ',':
                self.advance()
                return Token(COMMA, ',')
            if self.curr_char == '{':
                self.advance()
                self.skip_comment()
                continue
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
                return Token(FDIV, '/')
            if self.curr_char == '(':
                self.advance()
                return Token(LPAR, '(')
            if self.curr_char == ')':
                self.advance()
                return Token(RPAR, ')')
            else:
                self.error()

        return Token(EOF, None)


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
        self.op = op
        self.right = right


class Var(AST):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.val = token.val


class Type(AST):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.val = token.val


class VarDecl(AST):
    def __init__(self, var_node: Var, type_node: Type) -> None:
        self.var_node = var_node
        self.type_node = type_node


class Block(AST):
    def __init__(self, declarations: list[VarDecl], compound_statement: Compound) -> None:
        self.declarations = declarations
        self.compound_statement = compound_statement


class Program(AST):
    def __init__(self, name: Token, block: Block) -> None:
        self.name = name
        self.block = block


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
        elif token.type == REAL:
            self.eat(REAL)
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

        while self.curr_token.type in (MUL, DIV, FDIV):
            token = self.curr_token

            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
            elif token.type == FDIV:
                self.eat(FDIV)
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
        self.eat(PROGRAM)
        var_node = self.variable()
        name = var_node.val
        self.eat(SEMI)

        block = self.block()
        node = Program(name, block)
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

    def block(self) -> Block:
        decl = self.declarations()
        compound = self.compound_statement()
        block = Block(decl, compound)
        return block

    def declarations(self) -> list[VarDecl]:
        res = []

        if self.curr_token.type == VAR:
            self.eat(VAR)
            while self.curr_token.type == ID:
                var_decl = self.var_declaration()
                res.extend(var_decl)
                self.eat(SEMI)
        return res

    def var_declaration(self) -> list[VarDecl]:
        var_nodes = [Var(self.curr_token)]
        self.eat(ID)

        while self.curr_token.type == COMMA:
            self.eat(COMMA)
            var_nodes.append(Var(self.curr_token))
            self.eat(ID)

        self.eat(COLON)
        var_type = self.type_spec()
        declarations = [VarDecl(node, var_type) for node in var_nodes]
        return declarations

    def type_spec(self) -> Type:
        token = self.curr_token
        if token.type == INTEGER_TYPE:
            self.eat(INTEGER_TYPE)
        else:
            self.eat(REAL_TYPE)
            
        node = Type(token)
        return node
    
    def empty(self) -> NoOp:
        return NoOp()
    

class NodeVisitor:
    def visit(self, node: AST) -> object:
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: AST) -> None:
        raise NotImplementedError(f'No visit_{type(node).__name__} method defined')


class Interpreter(NodeVisitor):
    def __init__(self, parser: Parser) -> None:
        self.parser = parser
        self.GLOBAL_SCOPE = {}

    def visit_BinOp(self, node: BinOp) -> int | float:
        if node.op.type == ADD:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == SUB:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == DIV:
            return self.visit(node.left) // self.visit(node.right)
        elif node.op.type == FDIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_Num(self, node: Num) -> int | float:
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

        if var_name not in self.GLOBAL_SCOPE:
            raise NameError(repr(var_name))
        else:
            return self.GLOBAL_SCOPE[var_name]

    def visit_Program(self, node: Program) -> None:
        self.visit(node.block)

    def visit_Block(self, node: Block) -> None:
        for declaration in node.declarations:
            self.visit(declaration)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node: VarDecl) -> None:
        pass

    def visit_Type(self, node: Type) -> None:
        pass

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
        try:
            lexer = Lexer(text)
            parser = Parser(lexer)
            interpreter = Interpreter(parser)
            res = interpreter.interpret()
            print(interpreter.GLOBAL_SCOPE)
        except Exception as e:
            print(e)

if __name__ == '__main__':
    main()
