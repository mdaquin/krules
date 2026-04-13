# First-order Horn clause rule engine with unification
# Extends simple_propositional.py to support predicates with arguments
# Variables are identified by starting with an uppercase letter
# Facts must be ground (no variables); rules may contain variables

import re

_rename_counter = 0


def is_variable(s: str) -> bool:
  return bool(s) and s[0].isupper()


class Literal:
  def __init__(self, strrep: str):
    strrep = strrep.strip().replace(" ", "")
    self.negation = strrep[0] == '!'
    if self.negation:
      strrep = strrep[1:]
    m = re.match(r'(\w+)\(([^)]*)\)', strrep)
    if m:
      self.predicate = m.group(1)
      self.args = [a.strip() for a in m.group(2).split(',')]
    else:
      self.predicate = strrep
      self.args = []

  def apply(self, subst: dict) -> "Literal":
    """Return a copy with variables replaced according to subst, following chains."""
    new = Literal.__new__(Literal)
    new.negation = self.negation
    new.predicate = self.predicate
    new.args = []
    for a in self.args:
      while is_variable(a) and a in subst:
        a = subst[a]
      new.args.append(a)
    return new

  def rename(self, suffix: str) -> "Literal":
    """Return a copy with all variable names suffixed, to avoid capture."""
    new = Literal.__new__(Literal)
    new.negation = self.negation
    new.predicate = self.predicate
    new.args = [a + suffix if is_variable(a) else a for a in self.args]
    return new

  def is_ground(self) -> bool:
    return all(not is_variable(a) for a in self.args)

  def __str__(self) -> str:
    s = ("!" if self.negation else "") + self.predicate
    if self.args:
      s += "(" + ", ".join(self.args) + ")"
    return s

  def __eq__(self, other) -> bool:
    return (self.negation == other.negation and
            self.predicate == other.predicate and
            self.args == other.args)


def unify(l1: Literal, l2: Literal, subst: dict):
  """Unify two literals under subst. Returns the extended substitution, or None on failure."""
  if l1.negation != l2.negation or l1.predicate != l2.predicate or len(l1.args) != len(l2.args):
    return None
  s = dict(subst)
  for a1, a2 in zip(l1.args, l2.args):
    while is_variable(a1) and a1 in s: a1 = s[a1]
    while is_variable(a2) and a2 in s: a2 = s[a2]
    if a1 == a2: continue
    elif is_variable(a1): s[a1] = a2
    elif is_variable(a2): s[a2] = a1
    else: return None  # two distinct constants
  return s


def _split_body(body: str) -> list:
  """Split a rule body on commas, ignoring commas inside argument lists."""
  parts, current, depth = [], '', 0
  for ch in body:
    if ch == '(': depth += 1
    elif ch == ')': depth -= 1
    if ch == ',' and depth == 0:
      parts.append(current.strip())
      current = ''
    else:
      current += ch
  if current.strip():
    parts.append(current.strip())
  return parts


def _prolog_literal(s: str) -> str:
  """Convert a Prolog-style literal to our internal format: \\+(pred(X)) -> !pred(X)."""
  s = s.strip()
  m = re.match(r'\\\+\((.+)\)$', s)
  if m:
    return '!' + m.group(1).strip()
  return s


def _findSubstitutions(premises: list, facts: list, subst: dict) -> list:
  """Return all substitutions that simultaneously unify each premise with some fact."""
  if not premises: return [subst]
  results = []
  for fact in facts:
    new_subst = unify(premises[0], fact, subst)
    if new_subst is not None:
      results.extend(_findSubstitutions(premises[1:], facts, new_subst))
  return results


class Rule:
  def __init__(self, premises: list, conclusion: str):
    self.premise = [Literal(p) for p in premises]
    self.conclusion = Literal(conclusion)

  def rename(self) -> "Rule":
    """Return a copy with fresh variable names to avoid clashes across rule applications."""
    global _rename_counter
    _rename_counter += 1
    suffix = f"_{_rename_counter}"
    new = Rule.__new__(Rule)
    new.premise = [p.rename(suffix) for p in self.premise]
    new.conclusion = self.conclusion.rename(suffix)
    return new

  def __str__(self) -> str:
    return " ^ ".join(str(p) for p in self.premise) + " -> " + str(self.conclusion)


class KB:
  def __init__(self):
    self.rules = []
    self.facts = []

  def add_rule(self, premises: list, conclusion: str):
    self.rules.append(Rule(premises, conclusion))

  def add_fact(self, lit):
    if isinstance(lit, str): lit = Literal(lit)
    self.facts.append(lit)

  def valueOf(self, lit: Literal):
    """Return True if lit is asserted, False if its negation is, None if unknown."""
    for fact in self.facts:
      if fact.predicate == lit.predicate and fact.args == lit.args:
        return fact.negation == lit.negation
    return None

  def load(self, filename: str):
    """Load rules and facts from a file using a simplified Prolog-like syntax.

    Syntax:
      % comment
      head(X) :- body1(X), body2(X).   % rule
      fact(alice).                       % fact
      \\+(pred(X))                        % negation in rule body
    """
    with open(filename) as f:
      text = f.read()
    text = re.sub(r'%[^\n]*', '', text)
    for clause in text.split('.'):
      clause = clause.strip()
      if not clause:
        continue
      if ':-' in clause:
        head, body = clause.split(':-', 1)
        self.add_rule([_prolog_literal(p) for p in _split_body(body)],
                      _prolog_literal(head))
      else:
        self.add_fact(_prolog_literal(clause))

  def copy(self) -> "KB":
    new = KB()
    new.rules = self.rules[:]
    new.facts = self.facts[:]
    return new


def ForwardChaining(kb: KB, query: str):
  """Derive new ground facts to fixpoint; return truth value of query, or None on inconsistency."""
  Q = Literal(query)
  while True:
    if kb.valueOf(Q) is not None: return kb.valueOf(Q)
    new_facts = []
    for rule in kb.rules:
      for subst in _findSubstitutions(rule.premise, kb.facts, {}):
        conclusion = rule.conclusion.apply(subst)
        if not conclusion.is_ground(): continue
        val = kb.valueOf(conclusion)
        if val is True or conclusion in new_facts: continue
        if val is False:
          print(f"Inconsistency: {conclusion} contradicts existing facts")
          return None
        print(f"Applying {rule} with {subst}")
        new_facts.append(conclusion)
    if not new_facts: break
    kb.facts.extend(new_facts)
  val = kb.valueOf(Q)
  return val if val is not None else False


def BackwardChaining(kb: KB, G, subst: dict = None) -> bool:
  """Backward chaining with unification. G can be a string or list of Literals."""
  if isinstance(G, str): G = [Literal(G)]
  if subst is None: subst = {}
  if not G: return True

  g = G[0].apply(subst)
  NG = G[1:]

  # Try to satisfy g directly from known facts
  for fact in kb.facts:
    new_subst = unify(g, fact, subst)
    if new_subst is not None:
      if BackwardChaining(kb, NG, new_subst): return True

  # Try rules whose conclusion unifies with g
  for rule in kb.rules:
    r = rule.rename()
    new_subst = unify(r.conclusion, g, subst)
    if new_subst is None: continue

    # Skip rule if any ground premise is already contradicted
    ok = True
    for p in r.premise:
      if p.apply(new_subst).is_ground() and kb.valueOf(p.apply(new_subst)) is False:
        ok = False
        break
    if not ok: continue

    # Collect premises not yet satisfied as new subgoals
    open_premises = []
    for p in r.premise:
      if p.apply(new_subst).is_ground() and kb.valueOf(p.apply(new_subst)) is True: continue
      open_premises.append(p)
    new_goals = open_premises + list(NG)

    print(f"({r}) adds goals: ", end="")
    for p in open_premises: print(p.apply(new_subst), end=" ")
    print()

    if BackwardChaining(kb, new_goals, new_subst): return True

  return False


def InteractiveBackwardChaining(kb: KB, G, subst: dict = None) -> bool:
  """Backward chaining with unification and interactive user queries for unknown leaf facts.

  When a goal cannot be proven by any rule and is not a known fact, the user is
  asked directly. If the goal is non-ground at that point (a variable is still
  unbound), the user is first asked to supply a value for each unbound argument.
  """
  if isinstance(G, str): G = [Literal(G)]
  if subst is None: subst = {}
  if not G: return True

  g = G[0].apply(subst)
  NG = G[1:]

  # Short-circuit if g's truth value is already known, without re-asking the user.
  if g.is_ground() and kb.valueOf(g) is not None:
    if kb.valueOf(g): return InteractiveBackwardChaining(kb, NG, subst)
    return False

  # Try to satisfy g directly from known facts (also handles non-ground goals).
  for fact in kb.facts:
    new_subst = unify(g, fact, subst)
    if new_subst is not None:
      if InteractiveBackwardChaining(kb, NG, new_subst): return True

  # Try rules whose conclusion unifies with g.
  for rule in kb.rules:
    r = rule.rename()
    new_subst = unify(r.conclusion, g, subst)
    if new_subst is None: continue

    ok = True
    for p in r.premise:
      if p.apply(new_subst).is_ground() and kb.valueOf(p.apply(new_subst)) is False:
        ok = False; break
    if not ok: continue

    open_premises = []
    for p in r.premise:
      if p.apply(new_subst).is_ground() and kb.valueOf(p.apply(new_subst)) is True: continue
      open_premises.append(p)

    print(f"({r}) adds goals: ", end="")
    for p in open_premises: print(p.apply(new_subst), end=" ")
    print()

    # Two-step: prove premises first, then immediately cache g, then prove NG.
    # Caching g before attempting NG means it remains available for future queries
    # (e.g. proving bird(X) via has_feathers persists even if a higher goal fails).
    if InteractiveBackwardChaining(kb, open_premises, new_subst):
      g_ground = g.apply(new_subst)
      if g_ground.is_ground(): kb.add_fact(g_ground)
      if InteractiveBackwardChaining(kb, list(NG), new_subst): return True
      return False  # g is proven and cached, but NG failed

  # Only fall back to asking the user if g is a leaf predicate — one for which the
  # KB has no rules at all. Derived predicates (those with rules) that couldn't be
  # proven should simply fail rather than bother the user with a confusing question.
  has_rules = any(rule.conclusion.predicate == g.predicate and
                  rule.conclusion.negation == g.negation
                  for rule in kb.rules)
  if has_rules: return False

  # Leaf predicate: ask the user.
  # If g still has unbound variables, resolve them first.
  new_subst = dict(subst)
  for arg in g.args:
    if is_variable(arg):
      val = input(f"  Value for {arg} in {g}: ").strip()
      new_subst[arg] = val
  g = g.apply(new_subst)

  ui = input(f"  Is {g} true? [Y/N]: ").strip().upper()
  if ui == 'Y':
    kb.add_fact(g)
    if g.negation: return False          # goal was !p and user confirmed !p is true → p is false
    return InteractiveBackwardChaining(kb, NG, new_subst)
  else:
    kb.add_fact('!' + str(g) if not g.negation else str(g)[1:])
    return False
