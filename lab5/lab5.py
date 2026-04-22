from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Dict, Iterable, List, Sequence, Set, Tuple


Symbol = str
Production = Tuple[Symbol, ...]


@dataclass
class Grammar:
	nonterminals: Set[Symbol]
	terminals: Set[Symbol]
	productions: Dict[Symbol, Set[Production]]
	start_symbol: Symbol

	def copy(self) -> "Grammar":
		return Grammar(
			nonterminals=set(self.nonterminals),
			terminals=set(self.terminals),
			productions={lhs: set(rhs_set) for lhs, rhs_set in self.productions.items()},
			start_symbol=self.start_symbol,
		)

	@staticmethod
	def _tokenize_rhs(rhs: str) -> Production:
		rhs = rhs.strip()
		if rhs in {"", "e", "epsilon", "eps", "ε"}:
			return tuple()
		if " " in rhs:
			return tuple(token for token in rhs.split() if token)
		return tuple(rhs)

	@classmethod
	def from_rules(
		cls,
		nonterminals: Iterable[Symbol],
		terminals: Iterable[Symbol],
		rules: Dict[Symbol, Iterable[str | Sequence[Symbol]]],
		start_symbol: Symbol,
	) -> "Grammar":
		nts = set(nonterminals)
		ts = set(terminals)
		prods: Dict[Symbol, Set[Production]] = {nt: set() for nt in nts}

		for lhs, alternatives in rules.items():
			if lhs not in nts:
				raise ValueError(f"Unknown nonterminal on LHS: {lhs}")
			for alt in alternatives:
				if isinstance(alt, str):
					prod = cls._tokenize_rhs(alt)
				else:
					prod = tuple(alt)
				prods[lhs].add(prod)

		return cls(nts, ts, prods, start_symbol)

	@classmethod
	def from_text(
		cls,
		nonterminals: Iterable[Symbol],
		terminals: Iterable[Symbol],
		lines: Iterable[str],
		start_symbol: Symbol,
	) -> "Grammar":
		rules: Dict[Symbol, List[str]] = {}
		for raw_line in lines:
			line = raw_line.strip()
			if not line or line.startswith("#"):
				continue
			if "->" not in line:
				raise ValueError(f"Invalid rule line: {line}")
			lhs, rhs = [part.strip() for part in line.split("->", 1)]
			alternatives = [piece.strip() for piece in rhs.split("|")]
			rules.setdefault(lhs, []).extend(alternatives)
		return cls.from_rules(nonterminals, terminals, rules, start_symbol)

	def _is_nonterminal(self, symbol: Symbol) -> bool:
		return symbol in self.nonterminals

	def _new_nonterminal(self, base: str = "X") -> Symbol:
		i = 1
		while True:
			candidate = f"{base}{i}"
			if candidate not in self.nonterminals and candidate not in self.terminals:
				self.nonterminals.add(candidate)
				self.productions.setdefault(candidate, set())
				return candidate
			i += 1

	def eliminate_epsilon_productions(self) -> "Grammar":
		g = self.copy()

		nullable: Set[Symbol] = set()
		changed = True
		while changed:
			changed = False
			for lhs, rhs_set in g.productions.items():
				if lhs in nullable:
					continue
				if tuple() in rhs_set:
					nullable.add(lhs)
					changed = True
					continue
				for prod in rhs_set:
					if prod and all(sym in nullable for sym in prod):
						nullable.add(lhs)
						changed = True
						break

		new_productions: Dict[Symbol, Set[Production]] = {nt: set() for nt in g.nonterminals}

		for lhs, rhs_set in g.productions.items():
			for prod in rhs_set:
				if prod == tuple():
					continue

				nullable_positions = [i for i, sym in enumerate(prod) if sym in nullable]
				generated: Set[Production] = {prod}

				for size in range(1, len(nullable_positions) + 1):
					for idx_subset in combinations(nullable_positions, size):
						idx_subset_set = set(idx_subset)
						candidate = tuple(sym for i, sym in enumerate(prod) if i not in idx_subset_set)
						if candidate:
							generated.add(candidate)

				new_productions[lhs].update(generated)

		g.productions = new_productions
		return g

	def eliminate_unit_productions(self) -> "Grammar":
		g = self.copy()

		unit_pairs: Dict[Symbol, Set[Symbol]] = {nt: {nt} for nt in g.nonterminals}
		changed = True
		while changed:
			changed = False
			for a in g.nonterminals:
				for prod in g.productions.get(a, set()):
					if len(prod) == 1 and prod[0] in g.nonterminals:
						b = prod[0]
						if b not in unit_pairs[a]:
							unit_pairs[a].add(b)
							changed = True
						for c in unit_pairs[b]:
							if c not in unit_pairs[a]:
								unit_pairs[a].add(c)
								changed = True

		new_productions: Dict[Symbol, Set[Production]] = {nt: set() for nt in g.nonterminals}

		for a in g.nonterminals:
			for b in unit_pairs[a]:
				for prod in g.productions.get(b, set()):
					if len(prod) == 1 and prod[0] in g.nonterminals:
						continue
					new_productions[a].add(prod)

		g.productions = new_productions
		return g

	def eliminate_inaccessible_symbols(self) -> "Grammar":
		g = self.copy()

		reachable: Set[Symbol] = {g.start_symbol}
		changed = True
		while changed:
			changed = False
			for lhs in list(reachable):
				for prod in g.productions.get(lhs, set()):
					for sym in prod:
						if sym in g.nonterminals and sym not in reachable:
							reachable.add(sym)
							changed = True

		g.nonterminals = reachable
		g.productions = {lhs: set(rhs_set) for lhs, rhs_set in g.productions.items() if lhs in reachable}
		return g

	def eliminate_nonproductive_symbols(self) -> "Grammar":
		g = self.copy()

		productive: Set[Symbol] = set()
		changed = True
		while changed:
			changed = False
			for lhs, rhs_set in g.productions.items():
				if lhs in productive:
					continue
				for prod in rhs_set:
					if all((sym in g.terminals) or (sym in productive) for sym in prod):
						productive.add(lhs)
						changed = True
						break

		g.nonterminals = {nt for nt in g.nonterminals if nt in productive}
		g.productions = {lhs: set() for lhs in g.nonterminals}

		for lhs in list(self.productions.keys()):
			if lhs not in g.nonterminals:
				continue
			for prod in self.productions[lhs]:
				if all((sym in self.terminals) or (sym in g.nonterminals) for sym in prod):
					g.productions[lhs].add(prod)

		return g

	def to_cnf(self) -> "Grammar":
		g = self.copy()

		needs_new_start = any(
			g.start_symbol in prod for rhs_set in g.productions.values() for prod in rhs_set
		)
		if needs_new_start:
			old_start = g.start_symbol
			new_start = g._new_nonterminal("S")
			g.productions[new_start].update(g.productions[old_start])
			g.start_symbol = new_start

		terminal_map: Dict[Symbol, Symbol] = {}
		for lhs, rhs_set in list(g.productions.items()):
			updated_rhs: Set[Production] = set()
			for prod in rhs_set:
				if len(prod) >= 2:
					new_prod: List[Symbol] = []
					for sym in prod:
						if sym in g.terminals:
							if sym not in terminal_map:
								t_var = g._new_nonterminal("T")
								terminal_map[sym] = t_var
								g.productions[t_var].add((sym,))
							new_prod.append(terminal_map[sym])
						else:
							new_prod.append(sym)
					updated_rhs.add(tuple(new_prod))
				else:
					updated_rhs.add(prod)
			g.productions[lhs] = updated_rhs

		old_items = list(g.productions.items())
		g.productions = {lhs: set() for lhs in g.nonterminals}

		for lhs, rhs_set in old_items:
			for prod in rhs_set:
				if len(prod) <= 2:
					g.productions[lhs].add(prod)
					continue

				symbols = list(prod)
				current_lhs = lhs
				while len(symbols) > 2:
					new_nt = g._new_nonterminal("X")
					g.productions[current_lhs].add((symbols[0], new_nt))
					current_lhs = new_nt
					symbols = symbols[1:]
				g.productions[current_lhs].add(tuple(symbols))

		return g

	def normalize_to_cnf_with_steps(self) -> List[Tuple[str, "Grammar"]]:
		steps: List[Tuple[str, Grammar]] = []
		current = self.copy()
		steps.append(("Initial grammar", current))

		current = current.eliminate_epsilon_productions()
		steps.append(("After epsilon elimination", current))

		current = current.eliminate_unit_productions()
		steps.append(("After unit production elimination", current))

		current = current.eliminate_inaccessible_symbols()
		steps.append(("After inaccessible symbol elimination", current))

		current = current.eliminate_nonproductive_symbols()
		steps.append(("After nonproductive symbol elimination", current))

		current = current.to_cnf()
		steps.append(("Chomsky Normal Form", current))

		return steps

	def is_cnf(self) -> bool:
		for lhs, rhs_set in self.productions.items():
			if lhs not in self.nonterminals:
				return False
			for prod in rhs_set:
				if len(prod) == 1 and prod[0] in self.terminals:
					continue
				if len(prod) == 2 and prod[0] in self.nonterminals and prod[1] in self.nonterminals:
					continue
				return False
		return True

	def __str__(self) -> str:
		lines: List[str] = []
		lines.append(f"Vn = {sorted(self.nonterminals)}")
		lines.append(f"Vt = {sorted(self.terminals)}")
		lines.append(f"Start = {self.start_symbol}")
		lines.append("P:")

		for lhs in sorted(self.productions.keys()):
			rhs_parts = []
			for prod in sorted(self.productions[lhs]):
				rhs_parts.append("".join(prod) if prod else "epsilon")
			if rhs_parts:
				lines.append(f"  {lhs} -> {' | '.join(rhs_parts)}")
		return "\n".join(lines)


def variant_7_grammar() -> Grammar:
	return Grammar.from_rules(
		nonterminals={"S", "A", "B", "C", "E"},
		terminals={"a", "b"},
		rules={
			"S": ["bA", "B"],
			"A": ["a", "aS", "bAaAb"],
			"B": ["AC", "bS", "aAa"],
			"C": ["epsilon", "AB"],
			"E": ["BA"],
		},
		start_symbol="S",
	)


def run_self_tests() -> None:
	g = variant_7_grammar()
	steps = g.normalize_to_cnf_with_steps()
	cnf_grammar = steps[-1][1]

	assert cnf_grammar.is_cnf(), "Final grammar is not in CNF"

	sample = Grammar.from_text(
		nonterminals={"S", "A", "B"},
		terminals={"a", "b"},
		lines=[
			"S -> A B | b",
			"A -> a | epsilon",
			"B -> b",
		],
		start_symbol="S",
	)
	sample_cnf = sample.normalize_to_cnf_with_steps()[-1][1]
	assert sample_cnf.is_cnf(), "Generic parser grammar does not normalize to CNF"


def main() -> None:
	run_self_tests()

	grammar = variant_7_grammar()
	steps = grammar.normalize_to_cnf_with_steps()

	for title, step_grammar in steps:
		print(title)
		print(step_grammar)

	print("Validation: final grammar is CNF ->", steps[-1][1].is_cnf())


if __name__ == "__main__":
	main()
