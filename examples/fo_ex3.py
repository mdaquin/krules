import sys
sys.path.insert(0, '..')
from first_order import KB, ForwardChaining, BackwardChaining

kb = KB()
kb.load('dogs.pl')
print(f'Rules loaded: {len(kb.rules)}')
print(f'Facts loaded: {len(kb.facts)}')

print("\n=== Who is a dog? (Forward Chaining) ===")
# who is a dog?
for i in ['suzette', 'pepper', 'cider', 'ace']:
    kb2 = kb.copy()
    if ForwardChaining(kb2, f'dog({i})'): print(f'{i} is a dog')

print("\n=== Who is the son of whom? (Backward Chaining) ===")
for i in ['suzette', 'pepper', 'cider', 'ace']:
    for j in ['suzette', 'pepper', 'cider', 'ace']:
        kb2 = kb.copy()
        if BackwardChaining(kb2, f'son({i}, {j})'): print(f'{i} is the son of {j}')

print("\n=== Who is the mother of whom? (Backward Chaining) ===")
for i in ['suzette', 'pepper', 'cider', 'ace']:
    for j in ['suzette', 'pepper', 'cider', 'ace']:
        kb2 = kb.copy()
        if BackwardChaining(kb2, f'mother({i}, {j})'): print(f'{i} is the mother of {j}')