# Laboratory Work #2 - Finite Automaton

## Course: Formal Languages and Automata Theory
**Student:** Alexandrina Ciur  
**Variant:** 7

---

## Overview

A **finite automaton** is a fundamental mechanism in computer science used to represent and model various computational processes. Similar to state machines, finite automata have well-defined structures consisting of states, transitions, and acceptance conditions. The term "finite" signifies that these automata have a defined beginning (initial state) and a set of ending conditions (final states).

In automata theory, **determinism** characterizes how predictable a system behaves. When multiple states can be reached from a single transition, the automaton becomes non-deterministic. This laboratory work explores both deterministic (DFA) and non-deterministic (NDFA) finite automata, and demonstrates how to convert between these representations.

---

## Objectives

This laboratory work accomplishes the following goals:

1. **Implement a Finite Automaton** representation in Python
2. **Classify grammars** according to the Chomsky hierarchy
3. **Convert Finite Automaton to Regular Grammar**
4. **Determine if an FA is deterministic or non-deterministic**
5. **Implement NDFA to DFA conversion** using subset construction algorithm
6. **Bonus**: Graphical representation (optional)

---

## Variant Description

According to the assigned variant, the finite automaton is defined as follows:

**Given:**
- **Q** = {q0, q1, q2, q3} - Set of states
- **Σ** = {a, b} - Input alphabet
- **q0** - Initial state
- **F** = {q3} - Set of final/accepting states
- **δ** - Transition function:
  - δ(q0, a) = q1
  - δ(q1, a) = q1
  - δ(q1, b) = q2
  - δ(q2, b) = q2
  - δ(q2, b) = q3
  - δ(q3, a) = q1

**Note:** The transition function has **two rules** for δ(q2, b), making this a **non-deterministic** finite automaton (NDFA).

---

## Implementation

### 1. Finite Automaton Class

The `FiniteAutomaton` class represents the core structure of the automaton with all its components:

```python
class FiniteAutomaton:
    def __init__(self, states: Set[str], alphabet: Set[str], transitions: Dict, 
                 initial_state: str, final_states: Set[str]):
        self.states = states
        self.alphabet = alphabet
        self.transitions = transitions
        self.initial_state = initial_state
        self.final_states = final_states
```

The automaton is initialized with the variant specification:

```python
states = {'q0', 'q1', 'q2', 'q3'}
alphabet = {'a', 'b'}
initial_state = 'q0'
final_states = {'q3'}

transitions = {
    'q0': {'a': ['q1']},
    'q1': {'a': ['q1'], 'b': ['q2']},
    'q2': {'b': ['q2', 'q3']},  # Non-deterministic!
    'q3': {'a': ['q1']}
}
```

---

### 2. Determinism Check

The `is_deterministic()` method verifies whether the automaton is deterministic or non-deterministic by checking two key conditions:

**Implementation:**
```python
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
    
    return True
```

**Determinism Criteria:**
- Each state-symbol pair must have **at most one** transition
- No **epsilon (ε) transitions** are allowed
- All transitions must be explicitly defined

**Result for our variant:** The automaton is **NON-DETERMINISTIC** because state q2 with symbol 'b' has two possible transitions: {q2, q3}.

---

### 3. Conversion to Regular Grammar

The `to_regular_grammar()` method converts the finite automaton into an equivalent regular grammar using the following rules:

**Conversion Rules:**
- Each transition δ(qi, a) = qj becomes production: `Qi → aQj`
- If qj is a final state, also add: `Qi → a`
- The initial state becomes the start symbol

**Implementation:**
```python
def to_regular_grammar(self) -> Dict:
    non_terminals = set()
    for state in self.states:
        non_terminals.add(self._state_to_nonterminal(state))
    
    terminals = self.alphabet.copy()
    start_symbol = self._state_to_nonterminal(self.initial_state)
    
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
```

**Example Productions Generated:**
- Q0 → aQ1
- Q1 → aQ1 | bQ2
- Q2 → bQ2 | bQ3 | b (since Q3 is final)
- Q3 → aQ1

---

### 4. NDFA to DFA Conversion

The `convert_ndfa_to_dfa()` method implements the **subset construction algorithm** (also known as powerset construction). This algorithm eliminates non-determinism by creating DFA states that represent sets of NDFA states.

**Algorithm Overview:**
1. Start with the initial state as a singleton set
2. For each state set and each symbol, compute all reachable states
3. Create new DFA states from these state sets
4. Mark DFA states as final if they contain any NDFA final state
5. Continue until all reachable state sets are processed

**Implementation:**
```python
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
```

**Key Insights:**
- DFA states are named as sets: `{q0}`, `{q2,q3}`, etc.
- The problematic transition δ(q2, b) = {q2, q3} becomes a single DFA state `{q2,q3}`
- Every possible combination of NDFA states becomes a unique DFA state

---

### 5. Grammar Classification (Chomsky Hierarchy)

The `Grammar` class includes a method to classify grammars according to the **Chomsky hierarchy**:

**Implementation:**
```python
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
```

**Chomsky Hierarchy Levels:**

| Type | Name | Constraints | Example |
|------|------|-------------|---------|
| **Type 3** | Regular | A → aB or A → a | Q0 → aQ1 |
| **Type 2** | Context-Free | A → β (single non-terminal on left) | S → aSb |
| **Type 1** | Context-Sensitive | \|α\| ≤ \|β\| | αAβ → αγβ |
| **Type 0** | Unrestricted | No restrictions | Any production |

**Regular Grammar Check:**
```python
def _is_regular(self) -> bool:
    for left, rights in self.productions.items():
        if len(left) != 1 or left not in self.non_terminals:
            return False
        
        for right in rights:
            if not right:  # epsilon production
                continue
            
            # Check for right-linear: aB or a
            if len(right) == 1:
                if right not in self.terminals:
                    return False
            elif len(right) == 2:
                if right[0] not in self.terminals or right[1] not in self.non_terminals:
                    return False
            else:
                return False
    
    return True
```

---

## Execution Flow

The `main()` function demonstrates all functionality in sequence:

```python
def main():
    # Create the finite automaton
    fa = FiniteAutomaton(states, alphabet, transitions, initial_state, final_states)
    
    # Task 1: Display the FA
    fa.display()
    
    # Task 2: Check if deterministic
    is_dfa = fa.is_deterministic()
    
    # Task 3: Convert to Regular Grammar
    grammar_dict = fa.to_regular_grammar()
    grammar = Grammar(...)
    grammar.display()
    
    # Task 4: Convert NDFA to DFA
    dfa = fa.convert_ndfa_to_dfa()
    dfa.display()
```

---

## Results and Observations

### Original NDFA Analysis

The original automaton is **non-deterministic** due to the transition:
- δ(q2, b) = {q2, q3}

This means when in state q2 and reading symbol 'b', the automaton can choose to:
- Stay in q2 (loop)
- Move to q3 (accepting state)

### Generated Regular Grammar

The grammar produced from the NDFA is **Type 3 (Regular)**:
- **V_N** = {Q0, Q1, Q2, Q3}
- **V_T** = {a, b}
- **S** = Q0
- **P**:
  - Q0 → aQ1
  - Q1 → aQ1 | bQ2
  - Q2 → bQ2 | bQ3 | b
  - Q3 → aQ1

### Converted DFA

After applying the subset construction algorithm, the resulting DFA:
- Has more states than the original NDFA
- Is completely deterministic (verified by `is_deterministic()`)
- Accepts the same language as the original NDFA
- Every state-symbol pair has exactly one transition

---

## Language Accepted

The automaton accepts strings that:
1. **Start with 'a'** (transition from q0 to q1)
2. **Contain any combination of 'a' and 'b'** (loops and transitions)
3. **End with 'b'** (transition to final state q3)

**Valid examples:**
- `ab` 
- `aab` 
- `abb` 
- `aababb` 

**Invalid examples:**
- `ba`  (doesn't start with 'a')
- `aa`  (doesn't end with 'b')
- `b`  (doesn't start with 'a')

---

## Conclusion

Through this laboratory work, I gained a comprehensive understanding of finite automata and their practical implementation. I learned the fundamental distinction between deterministic and non-deterministic automata, and how the subset construction algorithm systematically eliminates non-determinism by creating DFA states that represent sets of NDFA states. The implementation demonstrated the practical trade-off between non-determinism (fewer states, multiple transitions) and determinism (more states, predictable behavior).

The most valuable insight was understanding the equivalence between finite automata and regular grammars. By implementing the conversion algorithms, I discovered how each transition directly corresponds to a production rule, establishing a clear mathematical relationship between these formalisms. The Chomsky hierarchy classification reinforced that grammars generated from finite automata always belong to Type 3 (Regular Grammars), perfectly aligning with the theoretical expectation that finite automata recognize regular languages. Adding graphical visualization using NetworkX and Matplotlib enhanced my understanding by making abstract concepts tangible, allowing me to visually verify correctness and trace string paths through the automaton.

From a software engineering perspective, I learned the importance of proper abstraction and modular design. Encapsulating automaton logic within well-defined classes made the code reusable and testable, while Python's type hints and data structures efficiently implemented mathematical concepts. This project strengthened both my theoretical understanding of automata theory and practical programming skills, bridging the gap between mathematical definitions and working code. The experience will be invaluable for understanding advanced topics in compiler design, regular expressions, and theoretical computer science.

---
