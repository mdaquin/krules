import sys
sys.path.insert(0, '..')
from first_order import KB, ForwardChaining, BackwardChaining

# The Iris knowledge base in first-order formalism.
# Rules are written once and apply to any individual X,
# unlike the propositional version where a separate KB is needed per sample.
kb = KB()

kb.add_rule(["wide(X)", "long(X)"],              "big(X)")
kb.add_rule(["narrow(X)", "short(X)"],           "small(X)")
kb.add_rule(["elongated(X)"],                    "long(X)")
kb.add_rule(["rounded(X)"],                      "wide(X)")
kb.add_rule(["elongated(X)", "smooth(X)"],                    "versicolor(X)")
kb.add_rule(["elongated(X)", "rough(X)", "small(X)"],         "setosa(X)")
kb.add_rule(["elongated(X)", "rough(X)", "big(X)"],           "versicolor(X)")
kb.add_rule(["rounded(X)", "rough(X)"],                       "versicolor(X)")
kb.add_rule(["rounded(X)", "smooth(X)", "small(X)"],          "versicolor(X)")
kb.add_rule(["rounded(X)", "smooth(X)", "big(X)"],            "virginica(X)")

# Sample 1: rounded, smooth, long -> virginica
kb.add_fact("rounded(sample1)")
kb.add_fact("smooth(sample1)")
kb.add_fact("long(sample1)")

# Sample 2: elongated, rough, narrow, short -> setosa
kb.add_fact("elongated(sample2)")
kb.add_fact("rough(sample2)")
kb.add_fact("narrow(sample2)")
kb.add_fact("short(sample2)")

# Forward chaining: derives all conclusions for all samples at once
print("=== Forward Chaining ===")
for species in ["virginica", "versicolor", "setosa"]:
  for sample in ["sample1", "sample2"]:
    kb2 = kb.copy()
    if ForwardChaining(kb2, f"{species}({sample})"): print(f"{sample} is {species}")

# Backward chaining: goal-directed, one query at a time
print("\n=== Backward Chaining ===")
for species in ["virginica", "versicolor", "setosa"]:
  for sample in ["sample1", "sample2"]:
    kb2 = kb.copy()
    if BackwardChaining(kb2, f"{species}({sample})"): print(f"{sample} is {species}")
