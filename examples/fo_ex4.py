import sys
sys.path.insert(0, '..')
from first_order import KB, InteractiveBackwardChaining

# Animal identification using interactive backward chaining.
#
# The KB contains only rules — no observable facts about the animal.
# The system will ask yes/no questions as it needs them to pursue each proof.
# Crucially, answers accumulate in the same KB across species attempts, so
# the user is never asked the same question twice.

kb = KB()
kb.load('animals.pl')

SPECIES = ['cheetah', 'tiger', 'giraffe', 'zebra', 'ostrich', 'penguin', 'albatross']
ANIMAL  = 'mystery'

print("Think of an animal. Answer Y or N to each question.")
print("(Answers are remembered — you won't be asked the same thing twice.)\n")

for species in SPECIES:
    print(f"--- Trying: {species} ---")
    if InteractiveBackwardChaining(kb, f'{species}({ANIMAL})'):
        print(f"\nThe animal is a {species}!")
        break
    print()
else:
    print("\nCould not identify the animal with the available rules.")

print("\nFacts learned during this session:")
for fact in kb.facts:
    print(f"  {fact}")
