# krules

A simple rule engine for learning purposes, available in two flavours:

- **`simple_propositional.py`** — propositional rules (atoms with no arguments)
- **`first_order.py`** — first-order rules with predicate arguments and unification (variables start with an uppercase letter, facts must be ground)

Both provide the same three inference algorithms:

| Algorithm | Description |
|---|---|
| `ForwardChaining` | Derives all reachable facts from the current KB until the query is answered |
| `BackwardChaining` | Goal-directed proof search, working backwards from the query through rules |
| `InteractiveBackwardChaining` | Like backward chaining, but asks the user for the value of any leaf fact that cannot be derived |

The first-order version additionally supports loading a KB from a file in a simplified Prolog-like syntax (`KB.load(filename)`).

## Limitations

- No Negation as Failure (NAF): negated premises only hold if the negated fact is explicitly asserted
- No cycle detection: recursive rules may cause infinite loops

## Propositional example

Inspired by the Iris dataset. Rules and facts are plain strings; negation is expressed with a `!` prefix.

```python
from simple_propositional import KB, ForwardChaining, BackwardChaining, InteractiveBackwardChaining

kb = KB()
kb.add_rule(["wide", "long"], "big")
kb.add_rule(["narrow", "short"], "small")
kb.add_rule(["elongated"], "long")
kb.add_rule(["rounded"], "wide")
kb.add_rule(["elongated", "smooth"], "versicolor")
kb.add_rule(["elongated", "rough", "small"], "setosa")
kb.add_rule(["elongated", "rough", "big"], "versicolor")
kb.add_rule(["rounded", "rough"], "versicolor")
kb.add_rule(["rounded", "smooth", "small"], "versicolor")
kb.add_rule(["rounded", "smooth", "big"], "virginica")

kb.add_fact("rounded")
kb.add_fact("smooth")
kb.add_fact("long")

if ForwardChaining(kb, "virginica"): print("virginica is true")
```

## First-order example

The same Iris rules written once apply to any number of samples via unification.

```python
from first_order import KB, ForwardChaining, BackwardChaining, InteractiveBackwardChaining

kb = KB()
kb.add_rule(["wide(X)", "long(X)"], "big(X)")
kb.add_rule(["narrow(X)", "short(X)"], "small(X)")
kb.add_rule(["elongated(X)"], "long(X)")
kb.add_rule(["rounded(X)"], "wide(X)")
kb.add_rule(["elongated(X)", "smooth(X)"], "versicolor(X)")
kb.add_rule(["elongated(X)", "rough(X)", "small(X)"], "setosa(X)")
kb.add_rule(["elongated(X)", "rough(X)", "big(X)"], "versicolor(X)")
kb.add_rule(["rounded(X)", "rough(X)"], "versicolor(X)")
kb.add_rule(["rounded(X)", "smooth(X)", "small(X)"], "versicolor(X)")
kb.add_rule(["rounded(X)", "smooth(X)", "big(X)"], "virginica(X)")

kb.add_fact("rounded(sample1)")
kb.add_fact("smooth(sample1)")
kb.add_fact("long(sample1)")

kb.add_fact("elongated(sample2)")
kb.add_fact("rough(sample2)")
kb.add_fact("narrow(sample2)")
kb.add_fact("short(sample2)")

if ForwardChaining(kb.copy(), "virginica(sample1)"): print("sample1 is virginica")
if ForwardChaining(kb.copy(), "setosa(sample2)"):   print("sample2 is setosa")
```

A KB can also be loaded from a file in simplified Prolog syntax:

```python
kb = KB()
kb.load("examples/iris.pl")
```

```prolog
% examples/iris.pl
big(X) :- wide(X), long(X).
small(X) :- narrow(X), short(X).
% ...
rounded(sample1).
smooth(sample1).
long(sample1).
```

## Interactive backward chaining example

When no rule can derive a leaf fact, `InteractiveBackwardChaining` asks the user directly.
Answers accumulate in the KB, so the same question is never asked twice.

```python
from first_order import KB, InteractiveBackwardChaining

kb = KB()
kb.load("examples/animals.pl")

for species in ["cheetah", "tiger", "giraffe", "zebra", "ostrich", "penguin", "albatross"]:
    if InteractiveBackwardChaining(kb, f"{species}(mystery)"):
        print(f"The animal is a {species}!")
        break
```

```
Is has_hair(mystery) true? [Y/N]: N
Is gives_milk(mystery) true? [Y/N]: N
Is has_pointed_teeth(mystery) true? [Y/N]: N
Is has_feathers(mystery) true? [Y/N]: Y
Is long_neck(mystery) true? [Y/N]: N
Is swims(mystery) true? [Y/N]: Y
Is black_and_white(mystery) true? [Y/N]: Y
The animal is a penguin!
```

## Examples

| File | Description |
|---|---|
| `examples/propositional.py` | Iris classification, propositional |
| `examples/fo_ex1.py` | Iris classification, first-order (rules defined in Python) |
| `examples/fo_ex2.py` | Iris classification, first-order (rules loaded from `iris.pl`) |
| `examples/fo_ex3.py` | Family/dog relationships, first-order |
| `examples/fo_ex4.py` | Animal identification using interactive backward chaining |
