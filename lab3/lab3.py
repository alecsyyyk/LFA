from enum import Enum, auto
from typing import List, Optional


class TokenType(Enum):
    INTEGER = auto()
    FLOAT = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    POWER = auto()
    LPAREN = auto()
    RPAREN = auto()
    COMMA = auto()
    SIN = auto()
    COS = auto()
    TAN = auto()
    SQRT = auto()
    LOG = auto()
    PI = auto()
    E = auto()
    IDENTIFIER = auto()
    ASSIGN = auto()
    SEMICOLON = auto()
    EOF = auto()


class Token:
    def __init__(self, token_type: TokenType, value: str, position: int):
        self.type = token_type
        self.value = value
        self.position = position
    
    def __repr__(self):
        return f"Token({self.type.name}, '{self.value}', pos={self.position})"
    
    def __str__(self):
        return f"{self.type.name}('{self.value}')"


class Lexer:
    KEYWORDS = {
        'sin': TokenType.SIN,
        'cos': TokenType.COS,
        'tan': TokenType.TAN,
        'sqrt': TokenType.SQRT,
        'log': TokenType.LOG,
        'pi': TokenType.PI,
        'e': TokenType.E,
    }
    
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.current_char = self.text[0] if text else None
    
    def error(self):
        raise Exception(f"Invalid character at position {self.position}")
    
    def advance(self):
        self.position += 1
        if self.position >= len(self.text):
            self.current_char = None
        else:
            self.current_char = self.text[self.position]
    

    
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
    
    def read_number(self) -> Token:
        start_pos = self.position
        num_str = ''
        has_dot = False
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                if has_dot:
                    break
                has_dot = True
            num_str += self.current_char
            self.advance()
        
        token_type = TokenType.FLOAT if has_dot else TokenType.INTEGER
        return Token(token_type, num_str, start_pos)
    

    
    def read_identifier(self) -> Token:
        start_pos = self.position
        id_str = ''
        
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            id_str += self.current_char
            self.advance()
        
        token_type = self.KEYWORDS.get(id_str.lower(), TokenType.IDENTIFIER)
        return Token(token_type, id_str, start_pos)
    
    def get_next_token(self) -> Token:
        self.skip_whitespace()
        
        if self.current_char is None:
            return Token(TokenType.EOF, '', self.position)
        
        if self.current_char.isdigit() or self.current_char == '.':
            return self.read_number()
        
        if self.current_char.isalpha() or self.current_char == '_':
            return self.read_identifier()
        
        start_pos = self.position
        char = self.current_char
        self.advance()
        
        if char == '+':
            return Token(TokenType.PLUS, '+', start_pos)
        elif char == '-':
            return Token(TokenType.MINUS, '-', start_pos)
        elif char == '*':
            return Token(TokenType.MULTIPLY, '*', start_pos)
        elif char == '/':
            return Token(TokenType.DIVIDE, '/', start_pos)
        elif char == '^':
            return Token(TokenType.POWER, '^', start_pos)
        elif char == '(':
            return Token(TokenType.LPAREN, '(', start_pos)
        elif char == ')':
            return Token(TokenType.RPAREN, ')', start_pos)
        elif char == ',':
            return Token(TokenType.COMMA, ',', start_pos)
        elif char == '=':
            return Token(TokenType.ASSIGN, '=', start_pos)
        elif char == ';':
            return Token(TokenType.SEMICOLON, ';', start_pos)
        else:
            self.error()
    
    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens


def print_tokens(tokens: List[Token]):
    print("\n" + "="*70)
    print("LEXICAL ANALYSIS RESULT")
    print("="*70)
    print(f"{'Position':<10} {'Token Type':<15} {'Value':<20}")
    print("-"*70)
    
    for token in tokens:
        if token.type != TokenType.EOF:
            print(f"{token.position:<10} {token.type.name:<15} {token.value:<20}")
    
    print("="*70 + "\n")


def run_tests():
    test_cases = [
        "3 + 5 * 2",
        "sin(3.14159) + cos(0)",
        "sqrt(16) + log(100)",
        "(2.5 + 3.8) * 4",
        "x = 5; y = 10",
        "sin(pi / 2) - cos(pi)",
        "tan(45) + sqrt(e)",
        "2^3 + 3^2 - 5",
        "(sin(x) + cos(y)) / 2",
        "result = sqrt(144) + log(1000)",
    ]
    
    print("\n" + "#"*70)
    print("# LEXER - EXTENDED CALCULATOR")
    print("# Supports: integers, floats, sin, cos, tan, sqrt, log, pi, e")
    print("#"*70)
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n[Test {i}] Input: {test_input}")
        
        try:
            lexer = Lexer(test_input)
            tokens = lexer.tokenize()
            print_tokens(tokens)
            
        except Exception as e:
            print(f"ERROR: {e}\n")


if __name__ == "__main__":
    run_tests()