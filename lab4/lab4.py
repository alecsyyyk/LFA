from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import List, Optional, Sequence


class RegexParseError(ValueError):
	"""Raised when the input regex does not fit the supported grammar."""


@dataclass
class Literal:
	value: str


@dataclass
class Concat:
	parts: List["Node"]


@dataclass
class Alternate:
	options: List["Node"]


@dataclass
class Repeat:
	node: "Node"
	min_times: int
	max_times: Optional[int]
	quantifier: str


Node = Literal | Concat | Alternate | Repeat


def normalize_pattern(pattern: str) -> str:
	"""Remove whitespace because the lab regexes are space-insensitive."""
	return "".join(ch for ch in pattern if not ch.isspace())


class RegexParser:
	"""
	Recursive-descent parser for a compact regex subset:
	- Literals: letters/digits/other non-meta chars
	- Grouping: (...)
	- Alternation: |
	- Quantifiers: *, +, ?, ^number
	"""

	def __init__(self, pattern: str) -> None:
		self.pattern = normalize_pattern(pattern)
		self.index = 0

	def parse(self) -> Node:
		if not self.pattern:
			raise RegexParseError("Empty regex is not supported.")
		node = self._parse_expression()
		if self._peek() is not None:
			raise RegexParseError(
				f"Unexpected character '{self._peek()}' at position {self.index}."
			)
		return node

	def _parse_expression(self) -> Node:
		terms = [self._parse_term()]
		while self._peek() == "|":
			self._consume("|")
			terms.append(self._parse_term())
		if len(terms) == 1:
			return terms[0]
		return Alternate(terms)

	def _parse_term(self) -> Node:
		factors: List[Node] = []
		while True:
			ch = self._peek()
			if ch is None or ch in ")|":
				break
			factors.append(self._parse_factor())

		if not factors:
			return Literal("")
		if len(factors) == 1:
			return factors[0]
		return Concat(factors)

	def _parse_factor(self) -> Node:
		atom = self._parse_atom()
		ch = self._peek()

		if ch == "*":
			self._consume("*")
			return Repeat(atom, 0, None, "*")
		if ch == "+":
			self._consume("+")
			return Repeat(atom, 1, None, "+")
		if ch == "?":
			self._consume("?")
			return Repeat(atom, 0, 1, "?")
		if ch == "^":
			self._consume("^")
			n = self._parse_number()
			return Repeat(atom, n, n, f"^{n}")
		return atom

	def _parse_atom(self) -> Node:
		ch = self._peek()
		if ch is None:
			raise RegexParseError("Unexpected end of regex.")

		if ch == "(":
			self._consume("(")
			expr = self._parse_expression()
			if self._peek() != ")":
				raise RegexParseError(
					f"Missing ')' at position {self.index}."
				)
			self._consume(")")
			return expr

		if ch in "|)*+?^":
			raise RegexParseError(
				f"Unexpected token '{ch}' at position {self.index}."
			)

		if ch == "\\":
			self._consume("\\")
			escaped = self._peek()
			if escaped is None:
				raise RegexParseError("Dangling escape at end of regex.")
			self.index += 1
			return Literal(escaped)

		self.index += 1
		return Literal(ch)

	def _parse_number(self) -> int:
		start = self.index
		while self._peek() is not None and self._peek().isdigit():
			self.index += 1
		if start == self.index:
			raise RegexParseError(f"Expected number at position {start}.")
		return int(self.pattern[start:self.index])

	def _peek(self) -> Optional[str]:
		if self.index >= len(self.pattern):
			return None
		return self.pattern[self.index]

	def _consume(self, token: str) -> None:
		if self._peek() != token:
			raise RegexParseError(
				f"Expected '{token}' at position {self.index}, found '{self._peek()}'."
			)
		self.index += 1


def node_to_text(node: Node) -> str:
	if isinstance(node, Literal):
		return node.value
	if isinstance(node, Concat):
		return "Concat(" + ", ".join(node_to_text(part) for part in node.parts) + ")"
	if isinstance(node, Alternate):
		return "Alt(" + " | ".join(node_to_text(opt) for opt in node.options) + ")"
	if isinstance(node, Repeat):
		return f"Repeat({node_to_text(node.node)}, {node.quantifier})"
	raise TypeError(f"Unsupported node type: {type(node)}")


def _generate_from_ast(
	node: Node,
	rng: random.Random,
	max_repeat: int,
	trace: Optional[List[str]] = None,
) -> str:
	if isinstance(node, Literal):
		if trace is not None:
			trace.append(f"Literal -> '{node.value}'")
		return node.value

	if isinstance(node, Concat):
		if trace is not None:
			trace.append(f"Concat with {len(node.parts)} parts")
		return "".join(
			_generate_from_ast(part, rng, max_repeat, trace) for part in node.parts
		)

	if isinstance(node, Alternate):
		idx = rng.randrange(len(node.options))
		if trace is not None:
			trace.append(
				f"Alternative choose {idx + 1}/{len(node.options)}"
			)
		return _generate_from_ast(node.options[idx], rng, max_repeat, trace)

	if isinstance(node, Repeat):
		effective_max = node.max_times
		if effective_max is None:
			effective_max = max_repeat

		if effective_max < node.min_times:
			raise ValueError(
				"Invalid repetition bounds after applying cap: "
				f"min={node.min_times}, max={effective_max}."
			)

		count = rng.randint(node.min_times, effective_max)
		if trace is not None:
			trace.append(
				f"Repeat {node.quantifier}: choose count={count} "
				f"(min={node.min_times}, max={effective_max})"
			)
		return "".join(
			_generate_from_ast(node.node, rng, max_repeat, trace)
			for _ in range(count)
		)

	raise TypeError(f"Unsupported node type: {type(node)}")


def generate_word(regex: str, max_repeat: int = 5, seed: Optional[int] = None) -> str:
	parser = RegexParser(regex)
	ast = parser.parse()
	rng = random.Random(seed)
	return _generate_from_ast(ast, rng, max_repeat)


def generate_words(
	regex: str,
	count: int = 5,
	max_repeat: int = 5,
	seed: Optional[int] = None,
) -> List[str]:
	parser = RegexParser(regex)
	ast = parser.parse()
	rng = random.Random(seed)

	results: List[str] = []
	seen = set()
	attempts = 0
	max_attempts = count * 40

	while len(results) < count and attempts < max_attempts:
		word = _generate_from_ast(ast, rng, max_repeat)
		attempts += 1
		if word not in seen:
			seen.add(word)
			results.append(word)

	return results


def processing_sequence(
	regex: str,
	max_repeat: int = 5,
	seed: Optional[int] = None,
) -> tuple[str, List[str]]:
	parser = RegexParser(regex)
	ast = parser.parse()
	rng = random.Random(seed)

	steps: List[str] = []
	steps.append(f"Input regex: {regex}")
	steps.append(f"Normalized regex: {normalize_pattern(regex)}")
	steps.append(f"Parsed AST: {node_to_text(ast)}")
	word = _generate_from_ast(ast, rng, max_repeat, steps)
	steps.append(f"Final generated word: {word}")
	return word, steps


def generate_for_regex_set(
	regexes: Sequence[str],
	words_per_regex: int = 5,
	max_repeat: int = 5,
	seed: Optional[int] = 42,
) -> dict[str, List[str]]:
	data: dict[str, List[str]] = {}
	for idx, regex in enumerate(regexes):
		local_seed = None if seed is None else seed + idx
		data[regex] = generate_words(
			regex,
			count=words_per_regex,
			max_repeat=max_repeat,
			seed=local_seed,
		)
	return data


def print_generation(regexes: Sequence[str], count: int, max_repeat: int, seed: int) -> None:
	generated = generate_for_regex_set(
		regexes,
		words_per_regex=count,
		max_repeat=max_repeat,
		seed=seed,
	)

	print("Generated sample sets:")
	for regex, words in generated.items():
		print(f"- {regex} -> {{{', '.join(words)}}}")


def main() -> None:
	parser = argparse.ArgumentParser(
		description="Dynamic regex-based word generator for lab exercises."
	)
	parser.add_argument(
		"--regex",
		action="append",
		help="Regex to generate from. Use multiple --regex values for a set.",
	)
	parser.add_argument(
		"--count",
		type=int,
		default=5,
		help="How many words to generate for each regex.",
	)
	parser.add_argument(
		"--max-repeat",
		type=int,
		default=5,
		help="Cap for '*' and '+' repetitions.",
	)
	parser.add_argument(
		"--seed",
		type=int,
		default=42,
		help="Random seed for reproducibility.",
	)
	parser.add_argument(
		"--trace",
		help="If provided, prints detailed processing for this regex.",
	)
	args = parser.parse_args()

	# Variant 3 from the provided task image.
	variant3_regexes = [
		"O(P|Q|R)+2(3|4)",
		"A*B(C|D|E)F(G|H|I)^2",
		"J+K(L|M|N)*O?(P|Q)^3",
	]

	target_regexes = args.regex if args.regex else variant3_regexes
	print_generation(
		regexes=target_regexes,
		count=args.count,
		max_repeat=args.max_repeat,
		seed=args.seed,
	)

	if args.trace:
		_, steps = processing_sequence(
			args.trace,
			max_repeat=args.max_repeat,
			seed=args.seed,
		)
		print("\nProcessing sequence:")
		for idx, step in enumerate(steps, start=1):
			print(f"{idx}. {step}")


if __name__ == "__main__":
	main()
