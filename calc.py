INTEGER, OPERATION, EOF = 'INTEGER', 'OPERATION', 'EOF'

class Token:
    def __init__(self, type: str, val: int):
        self.type = type
        self.val = val
    
    def __str__(self) -> str:
        return f"Token({self.type}, {self.val})"

class Interpreter:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.curr_token = None
        self.curr_char = self.text[self.pos]
    
    def error(self) -> Exception:
        raise Exception("error parsing input")

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
        if self.curr_char in "+-*/":    
            token = Token(OPERATION, self.curr_char)
            self.advance()
            return token

        self.error()

    def eat(self, type: str):
        if type == self.curr_token.type:
            self.curr_token = self.get_next_token()
        else:
            self.error()
    
    def expr(self):
        self.curr_token = self.get_next_token()
        left = self.curr_token
        self.eat(INTEGER)

        while self.curr_token.type != EOF:
            op = self.curr_token
            self.eat(OPERATION)
            right = self.curr_token
            self.eat(INTEGER)

            if op.val == '+':
                left.val = left.val + right.val
            elif op.val == '-':
                left.val = left.val - right.val
            elif op.val == '*':
                left.val = left.val * right.val
            else:
                left.val = left.val // right.val

        return left.val

inter = Interpreter("1+1 -3 * 100")
print(inter.expr())
