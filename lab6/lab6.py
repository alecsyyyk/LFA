from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
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


KEYWORDS = {
	"sin": TokenType.SIN,
	"cos": TokenType.COS,
	"tan": TokenType.TAN,
	"sqrt": TokenType.SQRT,
	"log": TokenType.LOG,
	"pi": TokenType.PI,
	"e": TokenType.E,
}


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


@dataclass
class Token:
	token_type: TokenType
	lexeme: str
	position: int

	def __str__(self) -> str:
		return f"{self.token_type.name}('{self.lexeme}')@{self.position}"


class LexerError(Exception):
	pass


class ParserError(Exception):
	pass


class Lexer:
	def __init__(self, text: str):
		self.text = text
		self.position = 0

	def tokenize(self) -> List[Token]:
		tokens: List[Token] = []

		while self.position < len(self.text):
			if self.text[self.position].isspace():
				self.position += 1
				continue

			chunk = self.text[self.position :]
			matched_token = self._match_token(chunk)
			if matched_token is None:
				char = self.text[self.position]
				raise LexerError(
					f"Invalid character '{char}' at position {self.position}"
				)

			token_type, lexeme = matched_token
			if token_type == TokenType.IDENTIFIER:
				lowered = lexeme.lower()
				token_type = KEYWORDS.get(lowered, TokenType.IDENTIFIER)

			tokens.append(Token(token_type, lexeme, self.position))
			self.position += len(lexeme)

		tokens.append(Token(TokenType.EOF, "", self.position))
		return tokens

	def _match_token(self, chunk: str) -> Optional[tuple[TokenType, str]]:
		for token_type, pattern in TOKEN_REGEX:
			match = pattern.match(chunk)
			if match:
				lexeme = match.group(0)
				return token_type, lexeme
		return None


@dataclass
class ASTNode:
	pass


@dataclass
class Program(ASTNode):
	statements: List[ASTNode]


@dataclass
class Assignment(ASTNode):
	name: str
	value: ASTNode


@dataclass
class BinaryOp(ASTNode):
	left: ASTNode
	operator: TokenType
	right: ASTNode


@dataclass
class UnaryOp(ASTNode):
	operator: TokenType
	operand: ASTNode


@dataclass
class FunctionCall(ASTNode):
	func: TokenType
	args: List[ASTNode]


@dataclass
class Number(ASTNode):
	value: str
	kind: TokenType


@dataclass
class Constant(ASTNode):
	kind: TokenType


@dataclass
class Identifier(ASTNode):
	name: str


class Parser:
	FUNCTION_TOKENS = {
		TokenType.SIN,
		TokenType.COS,
		TokenType.TAN,
		TokenType.SQRT,
		TokenType.LOG,
	}

	def __init__(self, tokens: List[Token]):
		self.tokens = tokens
		self.index = 0

	@property
	def current(self) -> Token:
		return self.tokens[self.index]

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

	def statement(self) -> ASTNode:
		if self._is_assignment_start():
			ident = self.consume(TokenType.IDENTIFIER)
			self.consume(TokenType.ASSIGN)
			value = self.expression()
			return Assignment(ident.lexeme, value)
		return self.expression()

	def expression(self) -> ASTNode:
		node = self.term()
		while self.current.token_type in (TokenType.PLUS, TokenType.MINUS):
			op = self.current.token_type
			self.advance()
			node = BinaryOp(node, op, self.term())
		return node

	def term(self) -> ASTNode:
		node = self.power()
		while self.current.token_type in (TokenType.MULTIPLY, TokenType.DIVIDE):
			op = self.current.token_type
			self.advance()
			node = BinaryOp(node, op, self.power())
		return node

	def power(self) -> ASTNode:
		node = self.unary()
		if self.current.token_type == TokenType.POWER:
			op = self.current.token_type
			self.advance()
			# Right-associative exponentiation: a ^ b ^ c == a ^ (b ^ c)
			node = BinaryOp(node, op, self.power())
		return node

	def unary(self) -> ASTNode:
		if self.current.token_type in (TokenType.PLUS, TokenType.MINUS):
			op = self.current.token_type
			self.advance()
			return UnaryOp(op, self.unary())
		return self.primary()

	def primary(self) -> ASTNode:
		token = self.current

		if token.token_type in (TokenType.INTEGER, TokenType.FLOAT):
			self.advance()
			return Number(token.lexeme, token.token_type)

		if token.token_type in (TokenType.PI, TokenType.E):
			self.advance()
			return Constant(token.token_type)

		if token.token_type == TokenType.IDENTIFIER:
			self.advance()
			return Identifier(token.lexeme)

		if token.token_type in self.FUNCTION_TOKENS:
			return self.function_call()

		if token.token_type == TokenType.LPAREN:
			self.consume(TokenType.LPAREN)
			node = self.expression()
			self.consume(TokenType.RPAREN)
			return node

		raise ParserError(
			f"Unexpected token {token.token_type.name} at position {token.position}"
		)

	def function_call(self) -> FunctionCall:
		func = self.current.token_type
		self.advance()
		self.consume(TokenType.LPAREN)

		args: List[ASTNode] = []
		if self.current.token_type != TokenType.RPAREN:
			args.append(self.expression())
			while self.current.token_type == TokenType.COMMA:
				self.consume(TokenType.COMMA)
				args.append(self.expression())

		self.consume(TokenType.RPAREN)
		return FunctionCall(func, args)

	def _is_assignment_start(self) -> bool:
		return (
			self.current.token_type == TokenType.IDENTIFIER
			and self._peek().token_type == TokenType.ASSIGN
		)

	def _peek(self) -> Token:
		peek_index = min(self.index + 1, len(self.tokens) - 1)
		return self.tokens[peek_index]

	def consume(self, expected: TokenType) -> Token:
		token = self.current
		if token.token_type != expected:
			raise ParserError(
				f"Expected {expected.name} at position {token.position}, "
				f"found {token.token_type.name}"
			)
		self.advance()
		return token

	def advance(self) -> None:
		if self.index < len(self.tokens) - 1:
			self.index += 1


def ast_node_label(node: ASTNode) -> str:
	if isinstance(node, Program):
		return "Program"
	if isinstance(node, Assignment):
		return f"Assignment(name={node.name})"
	if isinstance(node, BinaryOp):
		return f"BinaryOp(op={node.operator.name})"
	if isinstance(node, UnaryOp):
		return f"UnaryOp(op={node.operator.name})"
	if isinstance(node, FunctionCall):
		return f"FunctionCall(name={node.func.name})"
	if isinstance(node, Number):
		return f"Number(kind={node.kind.name}, value={node.value})"
	if isinstance(node, Constant):
		return f"Constant(name={node.kind.name})"
	if isinstance(node, Identifier):
		return f"Identifier(name={node.name})"
	return "UnknownNode"


def ast_children(node: ASTNode) -> List[ASTNode]:
	if isinstance(node, Program):
		return node.statements
	if isinstance(node, Assignment):
		return [node.value]
	if isinstance(node, BinaryOp):
		return [node.left, node.right]
	if isinstance(node, UnaryOp):
		return [node.operand]
	if isinstance(node, FunctionCall):
		return node.args
	return []


def build_ast_tree_lines(node: ASTNode, depth: int = 0) -> List[str]:
	indent = "  " * depth
	prefix = "- " if depth > 0 else ""
	lines = [f"{indent}{prefix}{ast_node_label(node)}"]

	for child in ast_children(node):
		lines.extend(build_ast_tree_lines(child, depth + 1))

	return lines


def format_ast(node: ASTNode) -> str:
	return "\n".join(build_ast_tree_lines(node))


def print_tokens_table(tokens: List[Token]) -> None:
	print("Tokens:")
	print("  # | Position | Type         | Lexeme")
	for idx, token in enumerate(tokens, start=1):
		if token.token_type == TokenType.EOF:
			continue
		print(
			f"  {idx:>2} | {token.position:>8} | "
			f"{token.token_type.name:<12} | {token.lexeme}"
		)


def parse_and_show(source: str) -> None:
	print(f"Source: {source}")
	try:
		lexer = Lexer(source)
		tokens = lexer.tokenize()
		parser = Parser(tokens)
		ast = parser.parse()

		print_tokens_table(tokens)
		print("AST:")
		print(format_ast(ast))
	except (LexerError, ParserError) as exc:
		print(f"Error: {exc}")


def run_tests() -> None:
	test_cases = [
		"3 + 5 * 2",
		"sin(pi / 2) - cos(pi)",
		"x = 5; y = sqrt(16) + log(100)",
		"result = (2 + 3)^2 - tan(45)",
		"sin(1, 2)",
		"z = -3.5 * (x + e)",
		"a = 2^3^2",
		"sin(pi / 2",
		"1 + @",
	]

	for index, source in enumerate(test_cases, start=1):
		print(f"\n[Test {index}]")
		parse_and_show(source)


def run_single_expression(expr: str) -> None:
	print("-" * 70)
	parse_and_show(expr)


def build_argument_parser() -> argparse.ArgumentParser:
	arg_parser = argparse.ArgumentParser(
		description="Regex lexer + parser + AST printer for LFA Lab 6"
	)
	arg_parser.add_argument(
		"--expr",
		type=str,
		help="Parse a single expression or statement list",
	)
	arg_parser.add_argument(
		"--run-tests",
		action="store_true",
		help="Run predefined demo test cases",
	)
	return arg_parser


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
