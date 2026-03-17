INTEGER, ADD, SUB, MUL, DIV, EOF, LPAR, RPAR = 'INTEGER', 'ADD', 'SUB', 'MUL', 'DIV', 'EOF', 'LPAR', 'RPAR'

class Token:
    def __init__(self, type: str, val: int):
        self.type = type
        self.val = val
    
    def __str__(self) -> str:
        return f"Token({self.type}, {self.val})"


class Lexer:
    def __init__(self, text: str):
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
            token = Token(ADD, self.curr_char)
            self.advance()
            return token
        if self.curr_char == '-':    
            token = Token(SUB, self.curr_char)
            self.advance()
            return token
        if self.curr_char == '*':    
            token = Token(MUL, self.curr_char)
            self.advance()
            return token
        if self.curr_char == '/':    
            token = Token(DIV, self.curr_char)
            self.advance()
            return token
        if self.curr_char == '(':
            token = Token(LPAR, self.curr_char)
            self.advance()
            return token
        if self.curr_char == ')':
            token = Token(RPAR, self.curr_char)
            self.advance()
            return token

        self.error()


class Interpreter:
    def __init__(self, text: str):
        self.lexer = Lexer(text)
        self.curr_token = self.lexer.get_next_token()
    
    def error(self):
        raise Exception("Invalid syntax")

    def eat(self, type: str) -> None:
        if type == self.curr_token.type:
            self.curr_token = self.lexer.get_next_token()
        else:
            self.error()
    
    def factor(self) -> int:
        token = self.curr_token
        if token.type == INTEGER:
            self.eat(INTEGER)
            return token.val
        if token.type == LPAR:
            self.eat(LPAR)
            res = self.expr()
            self.eat(RPAR)
            return res
            
        self.error()
    
    def term(self) -> int:
        res = self.factor()

        while self.curr_token.type in (MUL, DIV):
            token = self.curr_token

            if token.type == MUL:
                self.eat(MUL)
                res = res * self.factor()
            elif token.type == DIV:
                self.eat(DIV)
                res = res // self.factor()

        return res
    
    def expr(self) -> int:
        res = self.term()

        while self.curr_token.type in (ADD, SUB):
            token = self.curr_token

            if token.type == ADD:
                self.eat(ADD)
                res = res + self.term()
            elif token.type == SUB:
                self.eat(SUB)
                res = res - self.term()

        return res

def main():
    while True:
        try:
            text = input('calc> ')
        except EOFError:
            break
        if not text:
            continue
        interpreter = Interpreter(text)
        res = interpreter.expr()
        print(res)

if __name__ == '__main__':
    main()
