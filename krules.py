# a very basic rule+fact representation framework for
# propositional rules (not very optimised)
# can actually represent more than horn clauses ("not" possible in premise)
class Literal:
  def __init__(self, strrep: str):
    strrep = strrep.strip()
    strrep = strrep.replace(" ", "")
    if strrep[0] == '!':
      self.negation = True
      self.variable = strrep[1:]
    else:
      self.negation = False
      self.variable = strrep

  def __str__(self):
    if self.negation:return "!" + self.variable
    return self.variable

  def __eq__(self, other):
    return self.variable == other.variable and self.negation == other.negation

class Rule:
  def __init__(self, premise: list, conclusion: str):
    self.premise = []
    for premise in premise:
      self.premise.append(Literal(premise))
    self.conclusion = Literal(conclusion)

  def openPremise(self, kb: "KB") -> list:
    openL = []
    for premise in self.premise:
      if kb.valueOf(premise.variable) is None:
        openL.append(premise)
    return openL

  def __str__(self) -> str:
    s = ""
    for i,pre in enumerate(self.premise):
      if i!=0: s += " ^ "
      s += str(pre)
    s+=" -> "+str(self.conclusion)
    return s

class KB:
  def __init__(self):
    self.rules = []
    self.facts = []

  def add_rule(self, premisse: str, conclusion: str):
    self.rules.append(Rule(premisse, conclusion))

  def add_fact(self, lit):
    if type(lit) == str: lit = Literal(lit)
    self.facts.append(lit)

  def applicableRules(self) -> list:
    applicable = []
    for rule in self.rules:
      app = self.isApplicable(rule)
      if app is None: return None
      if app: applicable.append(rule)
    return applicable

  def isApplicable(self, rule: Rule) -> bool:
    # return true if the rule is applicable
    # false if the rule is not applicable
    # None if the current state is inconsistent
    # with the rule
    for premise in rule.premise:
      found = False
      for fact in self.facts:
        if premise == fact:
          found = True
          break
      if not found: return False
    for fact in self.facts:
      if fact.variable == rule.conclusion.variable:
        if fact == rule.conclusion: return False
        else: return None # premisse applicable but incompatible conclusion = inconsistency
    return True

  def compatibleRules(self, goal: Literal) -> list:
    # return the rules that have goal as conclusion
    # and which premisses are comptible with the facts
    compatible = []
    for rule in self.rules:
      if goal == rule.conclusion:
        for premise in rule.premise:
          for fact in self.facts:
            if fact.variable == premise.variable:
              if fact.negation != premise.negation: break
        compatible.append(rule)
    return compatible

  def valueOf(self, var: str) -> bool:
    for fact in self.facts:
      if fact.variable == var: return not fact.negation
    return None

  def copy(self) -> "KB":
    new = KB()
    new.rules = self.rules.copy()
    new.facts = self.facts.copy()
    return new
    
def ForwardChaining(kb: KB, Qu: str):
  # kb should include facts, Q is the name of the variable
  # of which we want to know the value
  Q = [kb]
  while len(Q) != 0:
    S = Q.pop()
    if S.valueOf(Qu) is not None: return S.valueOf(Qu)
    SR = S.applicableRules()
    if SR is None:
      print("Found an inconsistent state")
      print(SR)
      return None
    for rule in S.applicableRules():
      new = S.copy()
      print(f"Applying {rule}")
      new.facts.append(rule.conclusion)
      if rule.conclusion.variable == Qu: return new.valueOf(Qu)
      Q.append(new)
  return False

def BackwardChaining(kb: KB, G):
  # if G is a string, transform it into a list of Literals (goals)
  if type(G) == str: G = [Literal(G)]
  if len(G) == 0: return True
  if len(G) == 1 and kb.valueOf(G[0].variable) is not None:
    return kb.valueOf(G[0].variable) != G[0].negation
  for g in G:
    SR = kb.compatibleRules(g)
    NG = G.copy()
    NG.remove(g)
    if len(SR) == 0: return False
    found = False
    for rule in SR:
      NNG = NG.copy()
      adG = rule.openPremise(kb)
      print(f"({rule}) adds goals: ", end="")
      for a in adG: print(a, end=" ")
      print()
      NNG.extend(adG)
      if BackwardChaining(kb, NNG): 
        found=True
        break
    if not found: return False
  return True

# dirty implementation... we should be able to do better than that...
def InteractiveBackwardChaining(kb: KB, G):
  # if G is a string, transform it into a list of Literals (goals)
  if type(G) == str: G = [Literal(G)]
  if len(G) == 0: return True
  if len(G) == 1 and kb.valueOf(G[0].variable) is not None:
    return kb.valueOf(G[0].variable) != G[0].negation
  for g in G:
    SR = kb.compatibleRules(g)
    if len(SR) == 0:
      if kb.valueOf(g.variable) is not None:
        if kb.valueOf(g.variable): ui="Y"
        else: ui="N"
      else: ui = input(f"Type 'Y' if {g.variable} is true: ")
      if ui == "Y" and g.negation:
        kb.add_fact(g.variable)
        return False
      elif ui != "Y" and not g.negation:
        kb.add_fact("!"+g.variable)
        return False
      NG = G.copy()
      NG.remove(g)
      kb.add_fact(g)
      return InteractiveBackwardChaining(kb, NG)
    for rule in SR:
      NG = G.copy()
      NG.remove(g)
      adG = rule.openPremise(kb)
      print(f"({rule}) adds goals: ", end="")
      for a in adG: print(a, end=" ")
      print()
      NG.extend(adG)
      if not InteractiveBackwardChaining(kb, NG):
        if kb.valueOf(g.variable) is not None:
          if kb.valueOf(g.variable): ui="Y"
          else: ui="N"
        else: ui = input(f"Type 'Y' if {g.variable} is true: ")
        if ui == "Y" and g.negation:
          kb.add_fact(g.variable)
          return False
        elif ui != "Y" and not g.negation:
          kb.add_fact("!"+g.variable)
          return False
        kb.add_fact(g)
      else: kb.add_fact(g)
  return True

