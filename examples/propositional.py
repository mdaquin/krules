import sys
sys.path.insert(0, '..')
from simple_propositional import KB, ForwardChaining, BackwardChaining, InteractiveBackwardChaining
# the iris knowledge base
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

# the input facts for the question
kb.add_fact("rounded")
kb.add_fact("smooth")
kb.add_fact("long")

# asking the question
var ="virginica"
if ForwardChaining(kb, var): print(f"{var} is true")
else: print(f"we can not show that {var} is true")