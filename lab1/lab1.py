import random

class Grammar:
    def __init__(self, non_terminals, terminals, productions, start_symbol):
        self.VN = non_terminals
        self.VT = terminals
        self.P = productions
        self.S = start_symbol
    
    def generateString(self):
        result = self.S
        max_iterations = 1000
        iterations = 0
        
        while iterations < max_iterations:
            has_non_terminal = False
            for symbol in self.VN:
                if symbol in result:
                    has_non_terminal = True
                    break
            
            if not has_non_terminal:
                break
            
            for i, char in enumerate(result):
                if char in self.VN:
                    if char in self.P:
                        production = random.choice(self.P[char])
                        result = result[:i] + production + result[i+1:]
                        break
            
            iterations += 1
        
        return result
    
    def toFiniteAutomaton(self):
        states = set(self.VN)
        final_state = 'F_FINAL'
        states.add(final_state)
        
        alphabet = self.VT
        initial_state = self.S
        final_states = {final_state}
        transitions = {}
        
        for non_terminal, productions in self.P.items():
            for production in productions:
                if len(production) == 2:
                    terminal = production[0]
                    next_non_terminal = production[1]
                    if terminal in self.VT and next_non_terminal in self.VN:
                        transitions[(non_terminal, terminal)] = next_non_terminal
                elif len(production) == 1:
                    terminal = production[0]
                    if terminal in self.VT:
                        transitions[(non_terminal, terminal)] = final_state
        
        return FiniteAutomaton(states, alphabet, transitions, initial_state, final_states)


class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, initial_state, final_states):
        self.Q = states
        self.Sigma = alphabet
        self.delta = transitions
        self.q0 = initial_state
        self.F = final_states
    
    def stringBelongToLanguage(self, input_string):
        current_state = self.q0
        
        for symbol in input_string:
            if symbol not in self.Sigma:
                return False
            
            transition_key = (current_state, symbol)
            
            if transition_key in self.delta:
                current_state = self.delta[transition_key]
            else:
                return False
        
        return current_state in self.F
    
    def display(self):
        print("Finite Automaton:")
        print(f"States (Q): {self.Q}")
        print(f"Alphabet (Σ): {self.Sigma}")
        print(f"Initial state (q0): {self.q0}")
        print(f"Final states (F): {self.F}")
        print("Transitions (δ):")
        for (state, symbol), next_state in sorted(self.delta.items()):
            print(f"  δ({state}, {symbol}) = {next_state}")


def main():
    non_terminals = {'S', 'D', 'E', 'F', 'L'}
    terminals = {'a', 'b', 'c', 'd'}
    productions = {
        'S': ['aD'],
        'D': ['bE'],
        'E': ['cF', 'dL'],
        'F': ['dD'],
        'L': ['aL', 'bL', 'c']
    }
    start_symbol = 'S'
    
    grammar = Grammar(non_terminals, terminals, productions, start_symbol)
    
    print("="*50)
    print("Generated strings from grammar:")
    print("="*50)
    for i in range(5):
        generated_string = grammar.generateString()
        print(f"{i+1}. {generated_string}")
    
    print("\n" + "="*50)
    print("Finite Automaton:")
    print("="*50)
    
    fa = grammar.toFiniteAutomaton()
    fa.display()
    
    print("\n" + "="*50)
    print("String validation:")
    print("="*50)
    
    test_strings = [
        "abc",
        "abd",
        "abdc",
        "abcdc",
        "abcdbc",
        "xyz",
        "a",
        "ab",
        "abdabc",
    ]
    
    print("\nTesting generated strings:")
    for i in range(3):
        test_str = grammar.generateString()
        result = fa.stringBelongToLanguage(test_str)
        print(f"String '{test_str}': {'ACCEPTED' if result else 'REJECTED'}")
    
    print("\nTesting predefined strings:")
    for test_str in test_strings:
        result = fa.stringBelongToLanguage(test_str)
        print(f"String '{test_str}': {'ACCEPTED' if result else 'REJECTED'}")


if __name__ == "__main__":
    main()
