import sys
sys.path.insert(0, '..')
from first_order import KB, ForwardChaining, BackwardChaining

kb = KB()
kb.load('iris.pl')
print(f'Rules loaded: {len(kb.rules)}')
print(f'Facts loaded: {len(kb.facts)}')

print("\n=== Forward Chaining ===")
for species in ['virginica', 'versicolor', 'setosa']:
  for sample in ['sample1', 'sample2']:
    kb2 = kb.copy()
    if ForwardChaining(kb2, f'{species}({sample})'): print(f'{sample} is {species}')

print("\n=== Backward Chaining ===")
for species in ['virginica', 'versicolor', 'setosa']:
  for sample in ['sample1', 'sample2']:
    kb2 = kb.copy()
    if BackwardChaining(kb2, f'{species}({sample})'): print(f'{sample} is {species}')
