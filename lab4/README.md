# Lab 4 Dynamic Regular Expression Generator (Variant 3)

## 1. Regular Expressions Are
A regular expression (regex) is a formal pattern used to describe sets of strings over an alphabet.

In practical programming, regex is used to:
- validate input formats (emails, phone numbers, identifiers)
- search for text patterns in large files
- extract structured data from unstructured text
- transform text with find/replace rules
- define lexical patterns for simple parsers

For this lab, regex acts as a compact way to specify what words are valid.

## 2. Task Objective
The objective was to implement a generator that:
- receives one or more regex patterns as input
- interprets them dynamically (not hardcoded per pattern)
- generates valid words accepted by those patterns
- limits unbounded repetition (`*`, `+`) to 5 occurrences
- optionally shows the processing sequence (bonus)

## 3 Implementation 
The implementation lives in `lab4.py`, and the approach is pretty straightforward once you break it down. First, the regex pattern gets normalized—we strip out any unnecessary whitespace to keep things clean. Then, a recursive-descent parser converts the pattern into an abstract syntax tree, or AST for short. This tree structure represents the pattern's logical components: literals (actual characters), concatenations (things that go one after another), alternations (choices between options), and repetitions (things that can appear multiple times).

### 3.1 Supported Regex Features
The parser/generator supports:
- literals (letters, digits, and escaped special chars)
- grouping: `( ... )`
- alternation: `A|B`
- concatenation (implicit): `AB`
- quantifiers:
  - `*` -> from 0 to 5 times
  - `+` -> from 1 to 5 times
  - `?` -> 0 or 1 time
  - `^n` -> exactly `n` times



## 4. Variant 3 Expressions Used
Default expressions configured in the script:
1. `O(P|Q|R)+2(3|4)`
2. `A*B(C|D|E)F(G|H|I)^2`
3. `J+K(L|M|N)*O?(P|Q)^3`

The script also accepts custom regexes through CLI arguments.

## 5. Performed Actions

The implementation centers around a recursive-descent parser that transforms regex patterns into an abstract syntax tree (AST) using node types like `Literal`, `Concat`, `Alternate`, and `Repeat`. From this AST, a recursive generation algorithm walks through the structure to produce valid words, carefully capping unlimited repetitions to prevent unwieldy outputs. Duplicate filtering ensures variety when generating multiple examples, while a tracing feature tracks the step-by-step reasoning behind each generated word to satisfy the bonus requirement. Finally, the Variant 3 regex set is pre-configured for quick demonstration, making it easy to see the generator in action right away.

## 7. Conclusion

Building this project was not always easy. Some handwritten expressions were difficult to understand, so I used context and examples to find the correct meaning. Another problem was the combinatorial explosion caused by * and +, which can generate too many strings. To solve this, I limited repetitions to five, so the program stays efficient but still produces useful results. I also made sure the code is generic, not only working for specific examples, by using an AST structure.

In the end, the project became a reusable and flexible tool that can generate words from any supported regex pattern. It correctly handles operator precedence and avoids ambiguity thanks to a clear grammar. The program meets all requirements and works dynamically, meaning it can handle new patterns without changing the code.


