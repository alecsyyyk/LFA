
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class FiniteAutomaton:
    """
    Represents a Finite Automaton with transition functions.
    """
    
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict, 
                 initial_state: str, final_states: Set[str]):
    
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
    
    def is_deterministic(self) -> bool:
        
        for state in self.transitions:
            for symbol in self.transitions[state]:
                # Check if there are multiple transitions for same state-symbol pair
                next_states = self.transitions[state][symbol]
                if len(next_states) > 1:
                    return False
                
                # Check for epsilon transitions
                if symbol == 'ε' or symbol == '':
                    return False
        
        # Check if all state-symbol combinations are defined
        for state in self.states:
            for symbol in self.alphabet:
                if state not in self.transitions or symbol not in self.transitions[state]:
                    # Missing transitions also indicate non-determinism in some definitions
                    # but we'll consider it as deterministic if no multi-transitions
                    pass
        
        return True
    
    def to_regular_grammar(self) -> Dict:
        
        # Non-terminals are state names (converted to uppercase grammar notation)
        non_terminals = set()
        for state in self.states:
            non_terminals.add(self._state_to_nonterminal(state))
        
        # Terminals are the alphabet symbols
        terminals = self.alphabet.copy()
        
        # Start symbol is the initial state
        start_symbol = self._state_to_nonterminal(self.initial_state)
        
        # Generate productions from transitions
        productions = defaultdict(list)
        
        for state in self.transitions:
            nt_from = self._state_to_nonterminal(state)
            
            for symbol in self.transitions[state]:
                next_states = self.transitions[state][symbol]
                
                for next_state in next_states:
                    nt_to = self._state_to_nonterminal(next_state)
                    
                    # Add production: Qi -> aQj
                    productions[nt_from].append(symbol + nt_to)
                    
                    # If next_state is final, also add: Qi -> a
                    if next_state in self.final_states:
                        if symbol not in productions[nt_from]:
                            productions[nt_from].append(symbol)
        
        grammar = {
            'Non-terminals': non_terminals,
            'Terminals': terminals,
            'Productions': dict(productions),
            'Start': start_symbol
        }
        
        return grammar
    
    def _state_to_nonterminal(self, state: str) -> str:
        """Convert state name to non-terminal notation (e.g., q0 -> Q0)"""
        return state.replace('q', 'Q')
    
    def convert_ndfa_to_dfa(self) -> 'FiniteAutomaton':
       
        if self.is_deterministic():
            print("Already deterministic!")
            return self
        
        # Start with the initial state as a set
        dfa_start = frozenset([self.initial_state])
        dfa_states = set()
        dfa_transitions = {}
        dfa_final_states = set()
        
        # Queue of state sets to process
        to_process = [dfa_start]
        processed = set()
        
        while to_process:
            current_set = to_process.pop(0)
            
            if current_set in processed:
                continue
            
            processed.add(current_set)
            dfa_states.add(current_set)
            
            # Check if this is a final state (contains any NDFA final state)
            if any(state in self.final_states for state in current_set):
                dfa_final_states.add(current_set)
            
            # For each symbol, compute the next state set
            state_name = self._frozenset_to_name(current_set)
            dfa_transitions[state_name] = {}
            
            for symbol in self.alphabet:
                next_set = set()
                
                # Collect all possible next states from current state set
                for state in current_set:
                    if state in self.transitions and symbol in self.transitions[state]:
                        next_set.update(self.transitions[state][symbol])
                
                if next_set:
                    next_frozenset = frozenset(next_set)
                    next_name = self._frozenset_to_name(next_frozenset)
                    
                    dfa_transitions[state_name][symbol] = [next_name]
                    
                    if next_frozenset not in processed:
                        to_process.append(next_frozenset)
        
        # Convert frozensets to string names for final representation
        dfa_state_names = {self._frozenset_to_name(s) for s in dfa_states}
        dfa_final_names = {self._frozenset_to_name(s) for s in dfa_final_states}
        dfa_start_name = self._frozenset_to_name(dfa_start)
        
        dfa = FiniteAutomaton(
            states=dfa_state_names,
            alphabet=self.alphabet,
            transitions=dfa_transitions,
            initial_state=dfa_start_name,
            final_states=dfa_final_names
        )
        
        return dfa
    
    def _frozenset_to_name(self, fs: frozenset) -> str:
        """Convert frozenset of states to a readable name"""
        if not fs:
            return "∅"
        sorted_states = sorted(list(fs))
        return "{" + ",".join(sorted_states) + "}"
    
    def display(self):
        """Display the FA components in a readable format"""
        print("FINITE AUTOMATON")
        print(f"States (Q): {sorted(self.states)}")
        print(f"Alphabet (Σ): {sorted(self.alphabet)}")
        print(f"Initial State: {self.initial_state}")
        print(f"Final States (F): {sorted(self.final_states)}")
        print("\nTransitions (δ):")
        for state in sorted(self.transitions.keys()):
            for symbol in sorted(self.transitions[state].keys()):
                next_states = self.transitions[state][symbol]
                for next_state in next_states:
                    print(f"  δ({state}, {symbol}) = {next_state}")
      
class Grammar:
    """
    Represents a formal grammar with Chomsky hierarchy classification.
    """
    
    def __init__(self, non_terminals: Set[str], terminals: Set[str], 
                 productions: Dict[str, List[str]], start: str):
       
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.start = start
    
    def classify_chomsky(self) -> str:
       
        is_type_3 = self._is_regular()
        is_type_2 = self._is_context_free()
        is_type_1 = self._is_context_sensitive()
        
        if is_type_3:
            return "Type 3 (Regular Grammar)"
        elif is_type_2:
            return "Type 2 (Context-Free Grammar)"
        elif is_type_1:
            return "Type 1 (Context-Sensitive Grammar)"
        else:
            return "Type 0 (Unrestricted Grammar)"
    
    def _is_regular(self) -> bool:
        
        for left, rights in self.productions.items():
            # Left side must be a single non-terminal
            if len(left) != 1 or left not in self.non_terminals:
                return False
            
            for right in rights:
                if not right:  # epsilon production
                    continue
                
                # Check for right-linear: aB or a (terminal followed by optional non-terminal)
                if len(right) == 1:
                    # Must be terminal
                    if right not in self.terminals:
                        return False
                elif len(right) == 2:
                    # Must be: terminal + non-terminal
                    if right[0] not in self.terminals or right[1] not in self.non_terminals:
                        return False
                else:
                    return False
        
        return True
    
    def _is_context_free(self) -> bool:
        
        for left in self.productions.keys():
            # Left side must be a single non-terminal
            if len(left) != 1 or left not in self.non_terminals:
                return False
        return True
    
    def _is_context_sensitive(self) -> bool:
       
        for left, rights in self.productions.items():
            for right in rights:
                # Length of left must be <= length of right (except ε productions from start)
                if len(right) < len(left):
                    if not (left == self.start and right == ''):
                        return False
        return True
    
    def display(self):

        print("REGULAR GRAMMAR")
        print(f"Non-terminals (V_N): {sorted(self.non_terminals)}")
        print(f"Terminals (V_T): {sorted(self.terminals)}")
        print(f"Start Symbol (S): {self.start}")
        print("\nProductions (P):")
        for left, rights in sorted(self.productions.items()):
            for right in rights:
                print(f"  {left} → {right}")
        print(f"\nChomsky Classification: {self.classify_chomsky()}")
        

def main():
    
    # Define the given finite automaton
    # Q = {q0,q1,q2,q3}
    # Σ = {a,b}
    # F = {q3}
    # Transitions:
    states = {'q0', 'q1', 'q2', 'q3'}
    alphabet = {'a', 'b'}
    initial_state = 'q0'
    final_states = {'q3'}
    
    # Build transition function
    # Note: δ(q2,b) appears twice in the specification (→q3 and →q2), making it NDFA
    transitions = {
        'q0': {'a': ['q1']},
        'q1': {'a': ['q1'], 'b': ['q2']},
        'q2': {'b': ['q2', 'q3']},  # Non-deterministic!
        'q3': {'a': ['q1']}
    }
    
    # Create the finite automaton
    fa = FiniteAutomaton(states, alphabet, transitions, initial_state, final_states)
    
    # Task 1: Display the FA
    print("\n  1: Display Finite Automaton")
    fa.display()
    
    # Task 2: Check if deterministic or non-deterministic
    print("\n\n 2: Determinism Check")
    is_dfa = fa.is_deterministic()
    if is_dfa:
        print("Result: The automaton is DETERMINISTIC (DFA)")
    else:
        print("Result: The automaton is NON-DETERMINISTIC (NDFA)")
        print("\nReason: State 'q2' with symbol 'b' has multiple transitions:")
        print("  δ(q2, b) = {q2, q3}")
    
    # Task 3: Convert FA to Regular Grammar
    print("\n\n  3: Convert FA to Regular Grammar")
    grammar_dict = fa.to_regular_grammar()
    grammar = Grammar(
        grammar_dict['Non-terminals'],
        grammar_dict['Terminals'],
        grammar_dict['Productions'],
        grammar_dict['Start']
    )
    grammar.display()
    
    # Task 4: Convert NDFA to DFA
    print("\n\n 4: Convert NDFA to DFA")
    print("Applying subset construction algorithm...")
    dfa = fa.convert_ndfa_to_dfa()
    print("\nResulting DFA:")
    dfa.display()
    
    # Verify the DFA
    print("\n\n Verification:")
    print(f"Is the converted automaton deterministic? {dfa.is_deterministic()}")
    
    # Convert DFA to grammar to show it also produces valid grammar
    print("\n\n Grammar from Converted DFA")
    dfa_grammar_dict = dfa.to_regular_grammar()
    dfa_grammar = Grammar(
        dfa_grammar_dict['Non-terminals'],
        dfa_grammar_dict['Terminals'],
        dfa_grammar_dict['Productions'],
        dfa_grammar_dict['Start']
    )
    dfa_grammar.display()
    

if __name__ == "__main__":
    main()
