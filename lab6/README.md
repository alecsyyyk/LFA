# Parser and Building an Abstract Syntax Tree

Course: Formal Languages & Finite Automata.

## Theory
Parsing is the process of reading a sequence of tokens and determining whether that sequence follows the grammar of a language. In this work, lexical analysis transforms input text into categorized tokens, and syntactic analysis arranges those tokens into a hierarchical representation called an Abstract Syntax Tree (AST). The AST does not keep every low-level detail of the original text, but it preserves the essential structure of statements and expressions, which makes later stages such as semantic checks or evaluation easier to implement.

## Objectives
The main objective of this lab is to implement a complete flow from input text to syntactic structure, based on the previous lexical analyzer from Lab 3. The implementation introduces a TokenType definition to classify tokens, uses regular expressions to identify token categories, defines AST node structures for expressions and statements, and implements a recursive-descent parser that builds an AST for arithmetic expressions, function calls, constants, identifiers, and assignment statements.

## Implementation Description
The implementation has four main components.
First, token classification uses an enum and regular expressions. The lexer scans the input, identifies the longest valid tokens, recognizes keywords like sin, cos, sqrt, and log, and reports errors for invalid characters.

Second, the AST model defines node types such as Program, Assignment, BinaryOp, UnaryOp, FunctionCall, Number, Constant, and Identifier, allowing structured representation of expressions.

Third, the parser uses a recursive-descent approach to handle operator precedence, expressions, assignments, and function calls, while providing clear syntax error messages.

Finally, the program includes output handling and command-line support, allowing execution of expressions, running tests, and interactive use for better usability.

## Code Snippets
The following snippet shows the token type definition used by lexical analysis.

```python
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
```

The following snippet shows the lexer rule list where regular expressions identify token categories.

```python
TOKEN_REGEX = [
    (TokenType.FLOAT, re.compile(r"^(?:\d+\.\d+|\d+\.|\.\d+)")),
    (TokenType.INTEGER, re.compile(r"^\d+")),
    (TokenType.PLUS, re.compile(r"^\+")),
    (TokenType.MINUS, re.compile(r"^-")),
    (TokenType.MULTIPLY, re.compile(r"^\*")),
    (TokenType.DIVIDE, re.compile(r"^/")),
    (TokenType.POWER, re.compile(r"^\^")),
    (TokenType.LPAREN, re.compile(r"^\(")),
    (TokenType.RPAREN, re.compile(r"^\)")),
    (TokenType.COMMA, re.compile(r"^,")),
    (TokenType.ASSIGN, re.compile(r"^=")),
    (TokenType.SEMICOLON, re.compile(r"^;")),
    (TokenType.IDENTIFIER, re.compile(r"^[A-Za-z_][A-Za-z0-9_]*")),
]
```

The following snippet shows the parser entry point that builds a Program AST from tokenized input.

```python
def parse(self) -> Program:
    statements: List[ASTNode] = []

    while self.current.token_type != TokenType.EOF:
        statements.append(self.statement())
        if self.current.token_type == TokenType.SEMICOLON:
            self.consume(TokenType.SEMICOLON)
        elif self.current.token_type != TokenType.EOF:
            raise ParserError(
                f"Expected ';' or EOF at position {self.current.position}, "
                f"found {self.current.token_type.name}"
            )

    return Program(statements)
```

The following snippet shows the execution entry section that behaves as the main method in this Python implementation.

```python
if __name__ == "__main__":
    args = build_argument_parser().parse_args()
    if args.run_tests:
        run_tests()
    elif args.expr:
        run_single_expression(args.expr)
    else:
        print("No arguments provided. Enter one expression below (or type 'exit').")
        print("Tip: python lab6.py --expr \"x = 5; y = sqrt(16) + log(100)\"")
        user_expr = input("expr> ").strip()
        if user_expr.lower() not in {"", "exit", "quit"}:
            run_single_expression(user_expr)
```

## Results 
The implementation correctly recognizes valid mathematical expressions and assignment statements, then generates a readable AST that reflects precedence and nesting. It also reports meaningful lexical and syntactic errors, for example invalid symbols or missing parentheses, together with the position where the error occurs. A screenshot of sample execution in PowerShell can be attached here to show the generated tokens and AST output for a valid input expression.

## Conclusions
This lab demonstrates a complete and practical transition from lexical analysis to syntactic analysis by constructing an Abstract Syntax Tree. The final program is modular, because tokenization, parsing, and visualization are implemented as separate components, and it is extensible, because new operators or grammar rules can be added with localized code changes. The result is a solid base for future work such as semantic analysis, symbol-table management, or expression evaluation.
