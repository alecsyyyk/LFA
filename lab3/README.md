# Lab 3: Lexical Analysis - Lexer Implementation

## Overview

This lab implements a lexer (tokenizer/scanner) for mathematical expressions. The lexer performs lexical analysis by converting a string of characters into tokens, which is the first stage in compilation or interpretation.

## What is Lexical Analysis?

Lexical analysis breaks down a sequence of characters into meaningful tokens. A lexer reads input character by character, identifying patterns and grouping them into units. When it encounters a digit, it reads subsequent digits and possibly a decimal point to form a number. When it sees a letter, it reads the full word to determine if it's a function name like "sin" or a variable name. Special characters like operators are immediately recognized as tokens.

### Lexemes vs Tokens

A **lexeme** is the actual character sequence extracted from input ("sin", "3.14", "+"). A **token** contains the lexeme plus metadata: a type (INTEGER, FUNCTION, OPERATOR), the value, and the position in input. Both "42" and "1000" are different lexemes but share the same token type: INTEGER.

### Example

Input "sin(3.14) + 5" produces: SIN token → LPAREN → FLOAT(3.14) → RPAREN → PLUS → INTEGER(5) → EOF.

## Token Types Supported

### Numeric Tokens

**INTEGER** represents whole numbers like "5", "42", "1000". The lexer reads consecutive digits until reaching a non-digit character.

**FLOAT** represents decimal numbers like "3.14", "2.718", ".5", "42.". When the lexer encounters a decimal point while reading digits, it creates a FLOAT token.

### Operator Tokens

**PLUS** (+) for addition, **MINUS** (-) for subtraction, **MULTIPLY** (*) for multiplication, **DIVIDE** (/) for division, and **POWER** (^) for exponentiation. Each is a single-character token recognized immediately.

### Delimiter Tokens

**LPAREN** (() and **RPAREN** ()) control operation order and group terms. **COMMA** (,) separates function arguments. **SEMICOLON** (;) separates multiple statements.

### Function Tokens

**SIN**, **COS**, **TAN** are trigonometric functions. **SQRT** is square root, **LOG** is logarithm. When the lexer reads these words, it checks the keyword table to identify them as functions rather than variable names.

### Constant Tokens

**PI** represents π (≈3.14159) and **E** represents Euler's number (≈2.71828). These are recognized as special constants instead of variable names.

### Identifier Token

**IDENTIFIER** represents variable names not recognized as keywords. Must start with a letter or underscore, can contain letters, numbers, underscores. Examples: "x", "result", "_temp".

### Assignment and Control Tokens

**ASSIGN** (=) is used for variable assignment like "x = 5". **EOF** marks the end of input, signaling when tokenization is complete.

## Implementation Structure

### Token Class

Each Token object contains: **type** (TokenType enum like INTEGER, PLUS, SIN), **value** (the original string), and **position** (starting location in input). Example: "3.14" at position 4 creates Token(FLOAT, "3.14", 4).

### Lexer Class

The Lexer maintains a **keyword dictionary** mapping words like "sin" or "cos" to token types.

Key methods:
- `get_next_token()`: Returns one token by examining the current character
- `tokenize()`: Calls `get_next_token()` repeatedly to build a complete token list
- `read_number()`: Reads digits and at most one decimal point
- `read_identifier()`: Reads letters/digits/underscores, then checks keyword table
- `skip_whitespace()`: Advances past spaces and tabs

## How the Lexer Works

The lexer starts at position 0 and skips whitespace. It examines the current character to determine token type:
- Digit or '.' → read number
- Letter or '_' → read identifier/keyword
- Special character → create single-character token

**Numbers**: Collect digits and at most one decimal point. Create FLOAT if decimal found, otherwise INTEGER.

**Identifiers**: Collect letters/digits/underscores, then check keyword table. If found, create keyword token (SIN, COS, PI). Otherwise, create IDENTIFIER.

**Single characters**: '+', '-', '*', '/', '^', '(', ')', ',', '=', ';' are immediately recognized.

**Example**: "sin(45) + 2.5"
- pos 0: reads "sin" → SIN token
- pos 3: '(' → LPAREN
- pos 4: "45" → INTEGER
- pos 6: ')' → RPAREN
- pos 8: '+' → PLUS
- pos 10: "2.5" → FLOAT
- pos 13: end → EOF

## Running the Code

Run `python lab3.py` to execute ten test cases demonstrating the lexer. Each shows an input expression and a table of generated tokens with Position, Token Type, and Value columns.

Test cases include:
- Simple arithmetic: "3 + 5 * 2"
- Trigonometric functions: "sin(3.14159) + cos(0)"
- Math functions: "sqrt(16) + log(100)"
- Variable assignments: "x = 5; y = 10"
- Constants: "sin(pi / 2) - cos(pi)"
- Power operator: "2^3 + 3^2 - 5"
- Complex expressions: "(sin(x) + cos(y)) / 2"

## Key Concepts

**Separation of Concerns**: The lexer only identifies tokens, not syntax validity. It will tokenize "sin cos +" without error, leaving syntax checking to the parser.

**Pattern Recognition**: Numbers use digit sequences with optional decimal. Identifiers use letter/underscore followed by alphanumerics. Single-character tokens match exactly.

**Keywords vs Identifiers**: Both follow the same pattern. The lexer reads the full word, then checks the keyword table. Case-insensitive matching allows "sin", "Sin", or "SIN".

**Error Handling**: Unknown characters raise an error with position information. The lexer stops at the first error.

## The Lexer in Compiler Architecture

Compiler pipeline: Source Code → **[1. LEXER]** → Tokens → [2. Parser] → AST → [3. Semantic Analyzer] → [4. Code Generator] → Executable

The lexer is the first stage, transforming raw text into tokens. This separates character grouping from grammatical analysis, keeping the architecture modular.

## Conclusion

This lexer demonstrates lexical analysis by transforming text into tokens. It supports integers, floats, operators, functions (sin, cos, tan, sqrt, log), constants (pi, e), identifiers, and delimiters. The modular design separates token identification from syntax checking, creating a clean foundation for an extended calculator or programming language.

## Author

Lab 3 - LFA Course
Date: March 2026  

