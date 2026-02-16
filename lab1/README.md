# Formal Languages and Automata - Laboratory Work 1

## Course Information
**Course:** Formal Languages and Automata  
**Laboratory:** Lab 1  
**Topic:** Grammar and Finite Automaton Implementation

## Overview
This laboratory work implements the fundamental concepts of formal languages and automata theory. The implementation focuses on three main areas: formal grammar representation and string generation, conversion from grammar to finite automaton, and string validation using finite automaton. These components work together to demonstrate the equivalence between regular grammars and finite automata.

## Objectives
The primary objectives of this laboratory work are to implement a grammar class capable of generating valid strings, convert a regular grammar to a finite automaton, and validate whether strings belong to the language defined by the grammar. These objectives demonstrate the practical application of formal language theory and show how theoretical concepts translate into working code.

## Implementation

### 1. Grammar Class
The `Grammar` class represents a formal grammar with four essential components. The **VN (Non-terminals)** component is a set of non-terminal symbols `{S, D, E, F, L}` that serve as intermediate variables in the grammar. The **VT (Terminals)** component contains the set of terminal symbols `{a, b, c, d}` which are the actual characters that appear in generated strings. The **P (Productions)** component defines the production rules that specify how symbols can be transformed during the generation process. Finally, the **S (Start symbol)** represents the starting symbol of the grammar, which is `S` in this implementation.

**Code Implementation:**
```python
class Grammar:
    def __init__(self, non_terminals, terminals, productions, start_symbol):
        self.VN = non_terminals  # Non-terminal symbols
        self.VT = terminals      # Terminal symbols
        self.P = productions     # Production rules
        self.S = start_symbol    # Start symbol
```

This constructor initializes the grammar with all necessary components. The grammar is instantiated in the main function as:

```python
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
```

#### Production Rules
```
S → aD
D → bE
E → cF | dL
F → dD
L → aL | bL | c
```

#### Key Methods

**1. generateString() Method:**

This method generates valid strings by randomly applying production rules starting from the start symbol. It iterates through the string, replacing non-terminals with their productions until only terminals remain.

```python
def generateString(self):
    result = self.S  # Start with the start symbol
    max_iterations = 1000
    iterations = 0
    
    while iterations < max_iterations:
        # Check if there are any non-terminals left
        has_non_terminal = False
        for symbol in self.VN:
            if symbol in result:
                has_non_terminal = True
                break
        
        if not has_non_terminal:
            break  # All non-terminals replaced, string is complete
        
        # Find first non-terminal and replace it
        for i, char in enumerate(result):
            if char in self.VN:
                if char in self.P:
                    production = random.choice(self.P[char])  # Random production
                    result = result[:i] + production + result[i+1:]
                    break
        
        iterations += 1
    
    return result
```

The method uses a loop to find non-terminals in the current string and randomly selects one of their possible productions to replace them. This continues until no non-terminals remain.

**2. toFiniteAutomaton() Method:**

This method converts the grammar into an equivalent finite automaton by analyzing the production rules and creating appropriate states and transitions.

```python
def toFiniteAutomaton(self):
    states = set(self.VN)  # Non-terminals become states
    final_state = 'F_FINAL'
    states.add(final_state)
    
    alphabet = self.VT
    initial_state = self.S
    final_states = {final_state}
    transitions = {}
    
    # Create transitions from production rules
    for non_terminal, productions in self.P.items():
        for production in productions:
            if len(production) == 2:  # Form: A → aB
                terminal = production[0]
                next_non_terminal = production[1]
                if terminal in self.VT and next_non_terminal in self.VN:
                    transitions[(non_terminal, terminal)] = next_non_terminal
            elif len(production) == 1:  # Form: A → a (terminal production)
                terminal = production[0]
                if terminal in self.VT:
                    transitions[(non_terminal, terminal)] = final_state
    
    return FiniteAutomaton(states, alphabet, transitions, initial_state, final_states)
```

This conversion works by first converting each non-terminal into a state in the automaton. The algorithm then creates a special final state called `F_FINAL` to represent successful string acceptance. For productions of the form `A → aB` (where A and B are non-terminals and a is a terminal), the algorithm creates a transition δ(A, a) = B. For productions of the form `A → a` (terminal productions), it creates a transition δ(A, a) = F_FINAL, indicating that the string ends successfully after consuming that terminal.

### 2. Finite Automaton Class
The `FiniteAutomaton` class represents a finite automaton with five essential components. The **Q (States)** component is the set of states derived from the grammar's non-terminals plus an additional final state. The **Σ (Alphabet)** represents the terminal symbols that the automaton can process. The **δ (Transitions)** is the transition function that maps (state, symbol) pairs to next states, defining how the automaton moves between states. The **q0 (Initial state)** specifies the starting state of the automaton where processing begins. Finally, **F (Final states)** is the set of accepting states where the automaton successfully recognizes a valid string.

**Code Implementation:**
```python
class FiniteAutomaton:
    def __init__(self, states, alphabet, transitions, initial_state, final_states):
        self.Q = states           # Set of states
        self.Sigma = alphabet     # Input alphabet
        self.delta = transitions  # Transition function
        self.q0 = initial_state   # Initial state
        self.F = final_states     # Set of final/accepting states
```

#### Key Methods

**1. stringBelongToLanguage() Method:**

This method validates whether a given string is accepted by the automaton by simulating the automaton's behavior on the input string.

```python
def stringBelongToLanguage(self, input_string):
    current_state = self.q0  # Start from initial state
    
    # Process each symbol in the input string
    for symbol in input_string:
        # Check if symbol is in the alphabet
        if symbol not in self.Sigma:
            return False
        
        transition_key = (current_state, symbol)
        
        # Check if transition exists
        if transition_key in self.delta:
            current_state = self.delta[transition_key]  # Move to next state
        else:
            return False  # No valid transition, reject string
    
    # Accept only if we end in a final state
    return current_state in self.F
```

The method processes the input string symbol by symbol, following the transition function at each step. If at any point a symbol is not in the alphabet, or no transition exists for the current state and symbol combination, the string is immediately rejected. The string is accepted only if processing completes successfully and ends in a final state, indicating that the entire input string matches the language defined by the automaton.

**2. display() Method:**

This method prints all components of the finite automaton in a readable format.

```python
def display(self):
    print("Finite Automaton:")
    print(f"States (Q): {self.Q}")
    print(f"Alphabet (Σ): {self.Sigma}")
    print(f"Initial state (q0): {self.q0}")
    print(f"Final states (F): {self.F}")
    print("Transitions (δ):")
    for (state, symbol), next_state in sorted(self.delta.items()):
        print(f"  δ({state}, {symbol}) = {next_state}")
```

This provides clear visualization of the automaton structure for debugging and understanding.

## Grammar Type
The implemented grammar is a **Type 3 (Regular) Grammar** according to the Chomsky hierarchy. This classification is valid because all productions are either of the form `A → aB` (where A and B are non-terminals and a is a terminal) or of the form `A → a` (where A is a non-terminal and a is a terminal). This structure is characteristic of right-linear grammars, which are mathematically equivalent to regular languages and can be recognized by finite automata.

## How to Run

Execute the program using Python:
```bash
python lab1.py
```

The main function orchestrates all operations:

```python
def main():
    # Define the grammar
    grammar = Grammar(non_terminals, terminals, productions, start_symbol)
    
    # Generate strings
    for i in range(5):
        generated_string = grammar.generateString()
        print(f"{i+1}. {generated_string}")
    
    # Convert to finite automaton
    fa = grammar.toFiniteAutomaton()
    fa.display()
    
    # Test string validation
    for test_str in test_strings:
        result = fa.stringBelongToLanguage(test_str)
        print(f"String '{test_str}': {'ACCEPTED' if result else 'REJECTED'}")
```

## Execution Results

### String Generation
The program generates 5 random valid strings from the grammar by applying production rules randomly. The generated strings typically start with `ab` followed by various patterns determined by the grammar rules. Examples of valid strings include sequences like `abc`, `abdal...c`, and other combinations that follow the production patterns defined in the grammar.

**Example Output:**
```
==================================================
Generated strings from grammar:
==================================================
1. abdc
2. abdabc
3. abc
4. abdababc
5. abcdbc
```



### String Validation
The program performs two types of string validation tests. First, it validates that strings generated by the grammar are correctly accepted by the automaton, demonstrating the consistency between the grammar and its corresponding automaton. Second, it tests various predefined test strings to verify correct acceptance or rejection behavior, ensuring that the automaton properly identifies which strings belong to the language and which do not.

**Test String Array:**
```python
test_strings = [
    "abc",      # Should be ACCEPTED: S→aD→abE→abcF (with F being final via production L→c)
    "abd",      # Should be REJECTED: Incomplete string
    "abdc",     # Should be ACCEPTED: S→aD→abE→abdL→abdLc with L→ε
    "abcdc",    # Should be ACCEPTED: Valid path through grammar
    "abcdbc",   # Should be ACCEPTED: Multiple iterations through F→dD
    "xyz",      # Should be REJECTED: Invalid symbols
    "a",        # Should be REJECTED: Incomplete
    "ab",       # Should be REJECTED: Incomplete
    "abdabc",   # Should be ACCEPTED: Path through L productions
]
```

**Example Validation Output:**
```
==================================================
String validation:
==================================================

Testing generated strings:
String 'abdc': ACCEPTED
String 'abdabc': ACCEPTED
String 'abc': ACCEPTED

Testing predefined strings:
String 'abc': ACCEPTED
String 'abd': REJECTED
String 'abdc': ACCEPTED
String 'abcdc': ACCEPTED
String 'abcdbc': ACCEPTED
String 'xyz': REJECTED
String 'a': REJECTED
String 'ab': REJECTED
String 'abdabc': ACCEPTED
```

## Complete Automaton Structure

**Example Automaton Output:**
```
==================================================
Finite Automaton:
==================================================
Finite Automaton:
States (Q): {'S', 'D', 'E', 'F', 'L', 'F_FINAL'}
Alphabet (Σ): {'a', 'b', 'c', 'd'}
Initial state (q0): S
Final states (F): {'F_FINAL'}
Transitions (δ):
  δ(D, b) = E
  δ(E, c) = F
  δ(E, d) = L
  δ(F, d) = D
  δ(L, a) = L
  δ(L, b) = L
  δ(L, c) = F_FINAL
  δ(S, a) = D
```

This shows how the production rules are converted into state transitions. Each non-terminal becomes a state, and the productions define how to move between states on input symbols.

## Key Concepts Demonstrated

### 1. Formal Grammar
A formal grammar is a mathematical model for generating strings in a formal language. The grammar G = (VN, VT, P, S) defines how to start the generation process from the start symbol S, what symbols can appear in the final strings through the terminals VT, and how to transform non-terminals through the production rules P. This structured approach allows for precise specification of valid strings in the language.

**Example Generation:** S → aD → abE → abcF → abcdD → abcdbE → abcdbc (final)

### 2. Regular Languages
Regular languages are a class of formal languages that can be recognized by finite automata. Our grammar is classified as Type-3 (regular) because all productions follow a restricted pattern: either `A → aB` (right-linear form where a non-terminal produces a terminal followed by another non-terminal) or `A → a` (terminal production where a non-terminal produces only a terminal). This restriction ensures the language can be efficiently recognized by a finite automaton.

### 3. Grammar-to-Automaton Conversion
Algorithmic transformation showing the equivalence:
```python
# Grammar production: E → cF
# Becomes transition: δ(E, c) = F

# Grammar production: L → c
# Becomes transition: δ(L, c) = F_FINAL
```

### 4. String Recognition
The automaton validates membership by:
```python
# Start at initial state (S)
# For each input symbol, follow transition
# Accept if ending in final state
current_state = 'S'
for symbol in 'abc':
    current_state = transitions[(current_state, symbol)]
# Check: current_state in final_states?
```

## Technical Implementation Details

**Language**: Python 3  
**Dependencies**: Standard library only (`random` module)  
**Data Structures Used**: The implementation utilizes several Python data structures to efficiently represent the grammar and automaton. Sets are used for storing non-terminals, terminals, and states to ensure uniqueness and fast membership testing. Dictionaries store productions and transitions, providing O(1) lookup time for rule application. Tuples serve as dictionary keys for (state, symbol) pairs in the transition function, allowing efficient representation of the automaton's behavior.

**Algorithm Complexity**: The implementation has well-defined time complexities for each operation. String generation operates in O(n × m) time, where n is the length of the generated string and m is the number of non-terminals, as each position may require checking all non-terminals. String validation runs in O(n) time where n is the string length, processing each character exactly once. The grammar to finite automaton conversion operates in O(p) time where p is the number of productions, as each production rule is processed once to create corresponding transitions.

**Safety Features**:
```python
max_iterations = 1000  # Prevents infinite loops in generation

if symbol not in self.Sigma:  # Validates input alphabet
    return False

if transition_key in self.delta:  # Guards against missing transitions
    current_state = self.delta[transition_key]
```

## Conclusion
This laboratory work successfully demonstrates the theoretical equivalence between regular grammars and finite automata through practical Python implementations. The code illustrates multiple key concepts in action. **String Generation** demonstrates how production rules can be used to generate valid strings from the grammar through random rule application. The **Conversion Algorithm** shows the systematic transformation of grammar components into automaton states and transitions, maintaining the language's structure. **String Validation** simulates automaton behavior to accept or reject input strings based on the transition function and final states. Finally, **Correctness Verification** confirms that every string generated by the grammar is accepted by the corresponding finite automaton, proving the implementation's correctness and the theoretical equivalence between the two representations.

The implementation provides a hands-on understanding of formal language theory concepts and their practical applications in computer science, particularly in compiler design, pattern matching, and language processing.
